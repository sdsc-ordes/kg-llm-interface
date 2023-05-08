import os
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
        batch_size: The number of documents to vectorize and store in each batch.
    """

    chroma_url: str = "http://localhost:8000"
    collection_name: str = "test"
    batch_size: int = 50
    embedding_model_id: Optional[str] = None


class Location(BaseModel):
    """
    Attributes:
        instance_path: Path to instance graph(s). URL or RDF file.
        schema_path: Path to schema graph. URL or RDF file.
        sparql_endpoint: SPARQL endpoint URL. If provided, instance and schema paths are ignored.
        sparql_user: SPARQL endpoint user name. Only used if sparql_endpoint is provided.
        sparql_password: SPARQL endpoint password. Only used if sparql_endpoint is provided.
    """

    instances_path: Optional[Path] = None
    schema_path: Optional[Path] = None
    sparql_endpoint: Optional[str] = None
    sparql_user: Optional[str] = os.environ.get("SPARQL_USER")
    sparql_password: Optional[str] = os.environ.get("SPARQL_PASSWORD")
