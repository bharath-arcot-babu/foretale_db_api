import os
from sentence_transformers import SentenceTransformer  # For Sentence-Transformers & BGE

class EmbeddingsUtility:
    def get_sentence_transformer_all_minilm_l6_v2_embedding(text: str):
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return model.encode(text, convert_to_tensor=True).tolist()

    def get_bge_base_embedding(text: str):
        model = SentenceTransformer("BAAI/bge-base-en")
        return model.encode(text, convert_to_tensor=True).tolist()

    def get_bge_large_embedding(text: str):
        model = SentenceTransformer("BAAI/bge-large-en")
        return model.encode(text, convert_to_tensor=True).tolist()
