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

"""This flow builds a ChromaDB vector index from examples consisting of pairs of questions and SPARQL queries.

For each subject in the target graph, a document is generated. The document consists of:
* A human readable body made up of human readable questions
* SPARQL queries attached as metadata.

The documents are then stored in a vector database. The embedding is computed using the document body (questions),
and SPAQRL queries included as metadata. The index is persisted to disk and can be subsequently loaded into memory
for querying."""

from pathlib import Path
from typing import Optional, Tuple
from typing_extensions import Annotated
import uuid

from chromadb.api import ClientAPI, Collection
from dotenv import load_dotenv
from langchain.schema import Document
from more_itertools import chunked
from prefect import flow, task
from prefect import get_run_logger
import typer

from aikg.config import ChromaConfig
from aikg.config.common import parse_yaml_config
import aikg.utils.io as akio
import aikg.utils.chroma as akchroma


@task
def init_chromadb(
    host: str,
    port: int,
    collection_name: str,
    embedding_model: str,
    persist_directory: str,
) -> Tuple[ClientAPI, Collection]:
    """Prepare chromadb client."""
    client = akchroma.setup_client(host, port, persist_directory=persist_directory)
    coll = akchroma.setup_collection(client, collection_name, embedding_model)

    return client, coll


@task
def index_batch(batch: list[Document]):
    """Sends a batch of document for indexing in the vector store"""
    coll.add(
        ids=[str(uuid.uuid4()) for _ in batch],
        documents=[doc.page_content for doc in batch],
        metadatas=[doc.metadata for doc in batch],
    )


@flow
def chroma_build_examples_flow(
    chroma_input_dir: Path,
    chroma_cfg: ChromaConfig = ChromaConfig(),
):
    """Build a ChromaDB vector index from examples.

    Parameters
    ----------
    chroma_input_dir:
        Directory containing files with example question-query pairs. The files should be in sparql format, with the first line being the question as a comment.
    chroma_cfg:
        ChromaDB configuration.
    """
    load_dotenv()
    logger = get_run_logger()
    logger.info("INFO Started")
    # Connect to external resources
    global coll
    client, coll = init_chromadb(
        chroma_cfg.host,
        chroma_cfg.port,
        chroma_cfg.collection_examples,
        chroma_cfg.embedding_model,
        chroma_cfg.persist_directory,
    )

    # Create subject documents
    docs = akio.get_sparql_examples(
        input_path=chroma_input_dir,
    )

    # Vectorize and index documents by batches to reduce overhead
    logger.info(f"Indexing by batches of {chroma_cfg.batch_size} items")
    embed_counter = 0
    for batch in chunked(docs, chroma_cfg.batch_size):
        embed_counter += len(batch)
        index_batch(batch)
    logger.info(f"Indexed {embed_counter} items.")


def cli(
    chroma_input_dir: Annotated[
        Path,
        typer.Argument(
            help="Path to directory with example SPARQL queries",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    chroma_cfg_path: Annotated[
        Optional[Path],
        typer.Option(default=None, help="YAML file with Chroma client configuration."),
    ] = None,
):
    """Command line wrapper for SPARQL examples to ChromaDB index flow."""
    chroma_cfg = (
        parse_yaml_config(chroma_cfg_path, ChromaConfig)
        if chroma_cfg_path
        else ChromaConfig()
    )
    chroma_build_examples_flow(chroma_input_dir, chroma_cfg)


if __name__ == "__main__":
    typer.run(cli)
