import os
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Optional


class ChromaConfig(BaseModel):
    """
    Attributes:
        host:
            The host of the ChromaDB server. If set to "local", chroma will run in client-only mode.
        port:
            The port of the ChromaDB server.
        collection_name:
            The name of the ChromaDB collection to store the index in.
        embedding_model_id:
            The HuggingFace ID of the embedding model to use.
        batch_size:
            The number of documents to vectorize and store in each batch.
        persist_directory:
            If set to client-only mode, local path where the db is saved.
    """

    host: str = os.environ.get("CHROMA_HOST", "127.0.0.1")
    port: int = int(os.environ.get("CHROMA_PORT", "8000"))
    collection_name: str = os.environ.get("CHROMA_COLLECTION", "test")
    batch_size: int = int(os.environ.get("CHROMA_BATCH_SIZE", "50"))
    embedding_model: str = os.environ.get("CHROMA_MODEL", "all-mpnet-base-v2")
    persist_directory: str = os.environ.get("CHROMA_PERSIST_DIR", ".chroma/")
