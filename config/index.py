FAISS_INDEXES = {
    "test_case_1": {
        "index": "faiss_index/test_case_1.faiss",
        "metadata": "faiss_index/test_case_1.pkl"
    },
    "test_case_2": {
        "index": "faiss_index/test_case_2.faiss",
        "metadata": "faiss_index/test_case_2.pkl"
    }
}

def get_faiss_paths(test_case_name):
    """Retrieve FAISS index and metadata paths for a given test case."""
    return FAISS_INDEXES.get(test_case_name, None)
