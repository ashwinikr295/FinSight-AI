from vectorstore.vector_store import get_vector_store

def create_index(endpoint: str = None, api_key: str = None, index_name: str = None):
    """
    Initializes/verifies vector index (compatible with Azure AI Search and Local Vector Engine).
    """
    vs = get_vector_store()
    print("Vector Search index initialized successfully.")