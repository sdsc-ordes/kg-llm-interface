import chromadb
from chromadb.config import Settings
from chromadb.api import API, Collection


def setup_client(host: str, port: int, persist_directory: str = ".chroma") -> API:
    """Prepare chromadb client. If host is 'local', chromadb will run in client-only mode."""
    if host == "local":
        chroma_client = chromadb.PersistentClient(path=persist_directory)
    else:
        chroma_client = chromadb.HttpClient(host=host, port=str(port))
    return chroma_client


def setup_collection(
    client: API,
    collection_name: str,
    embedding_model: str,
) -> Collection:
    """Setup the connection to ChromaDB collection."""

    from chromadb.utils import embedding_functions

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    collection = client.get_or_create_collection(
        collection_name, embedding_function=embedding_function
    )
    return collection
