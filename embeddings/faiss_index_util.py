import pickle
import os
import faiss
from database.db_service import DatabaseService

class FAISSUtility:
    def __init__(self, project_test_id, dimension):
        self.dimension = dimension

        self.project_test_id = project_test_id

        self.db_service = DatabaseService()
        paths = self.fetch_index_details_from_db()

        self.index = None
        self.metadata = None
        self.index_path = paths["index_path"]
        self.metadata_path = paths["metadata_path"]
        

    def fetch_index_details_from_db(self):
        procedure_name = "dbo.SPROC_GET_VECTOR_EMBEDDING_STORAGE_DETAILS" 
        params = {
            'project_test_id'
        }
        tasks = self.db_service.execute_stored_procedure(procedure_name, params, isCommit=False)
        return tasks.get("data", [])
    
    def save_index(self, vectors, metadata):
        default_path = "/embeddings/storage/p2p-dup-001-01"
        self.index_path = self.index_path or default_path + ".index"
        self.metadata_path = self.metadata_path or default_path + ".pkl"

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors)
        faiss.write_index(self.index, self.index_path)

        if metadata:
            with open(self.metadata_path, "wb") as f:
                pickle.dump(metadata, f)

    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)

    def search(self, query_vector, k=3):
        if self.index is None:
            raise ValueError("Index is not loaded.")

        distances, indices = self.index.search(query_vector, k)
        return indices, distances