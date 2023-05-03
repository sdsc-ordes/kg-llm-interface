from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Optional


class Config(BaseModel):
    """
    Attributes:
        chroma_url: The URL of the ChromaDB server.
        collection_name: The name of the ChromaDB collection to store the index in.
        embedding_model_id: The HuggingFace ID of the embedding model to use.
    """

    chroma_url: str = "http://localhost:8000"
    collection_name: str = "test"
    embedding_model_id: Optional[str] = None


class Location(BaseModel):
    """
    Attributes:
        instance_path: Path to instance graph(s). URL or RDF file.
        schema_path: Path to schema graph. URL or RDF file.
    """

    instances_path: Path
    schema_path: Path
