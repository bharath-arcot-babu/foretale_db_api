import numpy as np
from embeddings.embeddings_util import EmbeddingsUtility
from embeddings.faiss_index_util import FAISSUtility
from database.db_service import DatabaseService


class P2PDUP00101:
    def __init__(self, project_test_id):
        self.project_test_id = project_test_id
        self.db_service = DatabaseService()
        self.embeddings_utility = EmbeddingsUtility()
        self.faiss_utility = FAISSUtility(project_test_id=project_test_id, dimension = 512)

    def fetch_items(self):
        procedure_name = "dbo.SPROC_GET_ITEMS"
        params = {}
        items = self.db_service.execute_stored_procedure(procedure_name, params, isCommit=False)
        return items.get("data", [])

    def process_items(self):
        vectors = []
        metadata = []
        items = self.fetch_items()

        for item in items:
            item_id = item["item_id"]
            text = item["item_name"]
            vector = self.embeddings_utility.get_sentence_transformer_all_minilm_l6_v2_embedding(text)
            vectors.append(vector)
            metadata.append({"item_id": item_id})

        self.faiss_utility.save_index(vectors, metadata)
        self.faiss_utility.load_index()

        item_name = "Laptop Charger"
        query_vector = np.array([self.embeddings_utility.get_sentence_transformer_all_minilm_l6_v2_embedding(item_name)], dtype="float32")
        duplicates = self.faiss_utility.search(query_vector, top_k=5)

        print("Possible Duplicates:", duplicates)



