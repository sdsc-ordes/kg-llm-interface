import chromadb
from chromadb.config import Settings
from chromadb.api import Collection
from fastapi import FastAPI
from llama_index.vector_stores import ChromaVectorStore
from requests import HTTPError
from typing import Optional
import urllib.parse


def get_chroma_client(host: str, port: int, persist_directory: Optional[str] = None):
    """Prepare chromadb client."""

    if host == "local":
        chroma_client = chromadb.Client(Settings(persist_directory=persist_directory))
    else:
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
    host: str, port: int, collection_name: str, embedding_model: str, persist_directory: Optional[str]
) -> Collection:
    """Setup the connection to ChromaDB collection."""

    from chromadb.utils import embedding_functions

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    client = get_chroma_client(host, port, persist_directory)
    collection = client.get_or_create_collection(
        collection_name, embedding_function=embedding_function
    )
    return collection
