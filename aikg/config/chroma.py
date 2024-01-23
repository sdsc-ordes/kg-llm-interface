# kg-llm-interface
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        collection_examples:
            The name of the ChromaDB collection to store examples in.
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
    collection_examples: str = os.environ.get("CHROMA_COLLECTION", "examples")
    batch_size: int = int(os.environ.get("CHROMA_BATCH_SIZE", "50"))
    embedding_model: str = os.environ.get("CHROMA_MODEL", "all-mpnet-base-v2")
    persist_directory: str = os.environ.get("CHROMA_PERSIST_DIR", ".chroma/")
