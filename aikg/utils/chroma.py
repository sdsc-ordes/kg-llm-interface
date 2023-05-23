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
