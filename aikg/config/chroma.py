import os
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Optional


class ChromaConfig(BaseModel):
    """
    Attributes:
        host: The host of the ChromaDB server.
        port: The port of the ChromaDB server.
        collection_name: The name of the ChromaDB collection to store the index in.
        embedding_model_id: The HuggingFace ID of the embedding model to use.
        batch_size: The number of documents to vectorize and store in each batch.
    """

    host: str = os.environ.get("CHROMA_HOST", "127.0.0.1")
    port: int = int(os.environ.get("CHROMA_PORT", "8000"))
    collection_name: str = os.environ.get("CHROMA_COLLECTION", "test")
    batch_size: int = 50
    # embedding_model: str = "all-MiniLM-L6-v2"
    embedding_model: str = "all-mpnet-base-v2"
