import chromadb
from chromadb.config import Settings
from chromadb.api import API, Collection
from fastapi import FastAPI
from llama_index.vector_stores import ChromaVectorStore
from requests import HTTPError
from typing import Optional
import urllib.parse


def setup_client(host: str, port: int, persist_directory: str = ".chroma") -> API:
    """Prepare chromadb client. If host is 'local', chromadb will run in client-only mode."""
    config = dict(
        anonymized_telemetry=False,
    )
    if host == "local":
        config |= dict(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
        )
    else:
        config |= dict(
            chroma_api_impl="rest",
            chroma_server_host=host,
            chroma_server_http_port=str(port),
        )
    chroma_client = chromadb.Client(
        Settings(
            **config,
        )
    )
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
