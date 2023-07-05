import chromadb
from chromadb.config import Settings
from fastapi import FastAPI
from llama_index.vector_stores import ChromaVectorStore
from requests import HTTPError
import urllib.parse


def get_chroma_client(host: str, port: int):
    """Prepare chromadb client."""

    # Connect to vector db server
    chroma_client = chromadb.Client(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host=host,
            chroma_server_http_port=str(port),
            anonymized_telemetry=False,
        )
    )
    return chroma_client


def setup_chroma(
    host: str, port: int, collection_name: str, embedding_model: str
) -> Collection:
    """Setup the connection to ChromaDB collection."""

    from chromadb.utils import embedding_functions

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    client = get_chroma_client(host, port)
    collection = client.get_collection(
        collection_name, embedding_function=embedding_function
    )
    return collection


def init_chromadb(
    host: str, port: int, collection_name: str, embedding_model: str
) -> ChromaVectorStore:
    """Prepare chromadb client."""
    from chromadb.utils import embedding_functions

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    chroma_client = get_chroma_client(host, port)
    try:
        chroma_client.delete_collection(collection_name)
    except (HTTPError, Exception) as _:
        pass
    collection = chroma_client.get_or_create_collection(
        collection_name, embedding_function=embedding_function
    )
    return ChromaVectorStore(chroma_collection=collection)
