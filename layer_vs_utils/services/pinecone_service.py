import json
import uuid
import pinecone
from typing import Dict, List, Optional, Any
from layer_db_utils.services.db_service import DatabaseService
from layer_vs_utils.config import Config

db_service = DatabaseService()

class PineconeService:
    """
    Service class for interacting with Pinecone vector database.
    """
    
    def __init__(
        self,
        index_name: Optional[str] = None
    ):
        """
        Initialize the Pinecone service.
        
        Args:
            api_key: Pinecone API key. If None, uses PINECONE_API_KEY environment variable.
            environment: Pinecone environment. If None, uses PINECONE_ENVIRONMENT environment variable.
            index_name: Pinecone index name. If None, uses PINECONE_INDEX_NAME environment variable.
        """

        self.api_key = Config.PINECONE_API_KEY
        self.region = Config.PINECONE_REGION
        self.index_name = index_name
        
        if not self.api_key or not self.region or not self.index_name:
            raise ValueError(
                "Missing Pinecone configuration. Please provide api_key, region, and index_name "
                "either as parameters or as environment variables."
            )
        
        # Initialize Pinecone with new API
        self.pc = pinecone.Pinecone(api_key=self.api_key)
        
        # Connect to the index
        self.index = self.pc.Index(self.index_name)
    
    def insert_embeddings(
        self,
        embeddings: List[List[float]],
        metadata_list: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        namespace: str = "",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Insert embeddings with metadata to Pinecone.
        
        Args:
            embeddings: List of embedding vectors (each is a list of floats).
            metadata_list: List of metadata dictionaries corresponding to each embedding.
            ids: Optional list of IDs for the vectors. If not provided, random UUIDs will be generated.
            namespace: Optional namespace for the vectors.
            batch_size: Number of vectors to insert in each batch.
            
        Returns:
            A dictionary containing insertion statistics.
        """
        # Insert in batches
        stats = {
            "total_vectors": 0,
            "batches_sent": 0,
            "vectors_inserted": 0,
            "error": None,
            "failed_at_batch": None,
        }
        
        try:
            if len(embeddings) != len(metadata_list):
                raise ValueError("Number of embeddings must match number of metadata dictionaries")
            
            # Generate IDs if not provided
            if not ids:
                ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]
            elif len(ids) != len(embeddings):
                raise ValueError("Number of IDs must match number of embeddings")
            
            # Prepare vectors for insertion
            vectors_to_insert = []
            for i, (values, meta) in enumerate(zip(embeddings, metadata_list)):
                vector_id = ids[i]
                vectors_to_insert.append({
                    'id': vector_id,
                    'values': values,
                    'metadata': meta
                })
            
            stats["total_vectors"] = len(vectors_to_insert)

            for i in range(0, len(vectors_to_insert), batch_size):
                batch = vectors_to_insert[i:i+batch_size]
                try:
                    self.index.upsert(vectors=batch, namespace=namespace)
                    stats["batches_sent"] += 1
                    stats["vectors_inserted"] += len(batch)

                except Exception as e:
                    stats["error"] = str(e)
                    stats["failed_at_batch"] = stats["batches_sent"] + 1
                    break

        except Exception as e:
            stats["error"] = str(e)

        finally:
            return stats

    def query_embeddings(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_vector: The embedding vector to search for.
            top_k: Number of results to return.
            namespace: Optional namespace to search in.
            filter: Optional filter dictionary to apply.
            include_metadata: Whether to include metadata in the results.
            
        Returns:
            Query results from Pinecone.
        """
        return self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata
        )
    
    def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete vectors from Pinecone.
        
        Args:
            ids: List of vector IDs to delete.
            delete_all: Whether to delete all vectors.
            namespace: Optional namespace to delete from.
            filter: Optional filter to apply when deleting.
            
        Returns:
            Deletion result from Pinecone.
        """
        if delete_all:
            return self.index.delete(delete_all=True, namespace=namespace)
        elif ids:
            return self.index.delete(ids=ids, namespace=namespace)
        elif filter:
            return self.index.delete(filter=filter, namespace=namespace)
        else:
            raise ValueError("Must provide either ids, filter, or set delete_all=True")





