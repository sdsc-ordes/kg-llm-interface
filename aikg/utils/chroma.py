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

import chromadb
from chromadb.config import Settings
from chromadb.api import ClientAPI, Collection


def setup_client(host: str, port: int, persist_directory: str = ".chroma") -> ClientAPI:
    """Prepare chromadb client. If host is 'local', chromadb will run in client-only mode."""
    if host == "local":
        chroma_client = chromadb.PersistentClient(path=persist_directory)
    else:
        chroma_client = chromadb.HttpClient(host=host, port=str(port))
    return chroma_client


def setup_collection(
    client: ClientAPI,
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
