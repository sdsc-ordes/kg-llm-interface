import chromadb
from chromadb.config import Settings
from fastapi import FastAPI
from llama_index.vector_stores import ChromaVectorStore
from requests import HTTPError
import urllib.parse


def get_chroma_client(chroma_url: str):
    """Prepare chromadb client."""

    # Connect to vector db server
    url = urllib.parse.urlsplit(chroma_url)
    chroma_host, chroma_port = (url.hostname, url.port)
    chroma_client = chromadb.Client(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host=chroma_host,
            chroma_server_http_port=chroma_port,
            anonymized_telemetry=False,
        )
    )
    return chroma_client
