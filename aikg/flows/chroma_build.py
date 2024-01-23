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

"""This flow builds a ChromaDB vector index from RDF data in a SPARQL endpoint.

For each subject in the target graph, a document is generated. The document consists of:
* A human readable body made up of the annotations (rdfs:comment, rdf:label) associated with the subject.
* Triples with the subject attached as metadata.

The documents are then stored in a vector database. The embedding is computed using the document body,
and triples included as metadata. The index is persisted to disk and can be subsequently loaded into memory
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
from rdflib import ConjunctiveGraph, Graph
from SPARQLWrapper import SPARQLWrapper
import typer

from aikg.config import ChromaConfig, SparqlConfig
from aikg.config.common import parse_yaml_config
import aikg.utils.rdf as akrdf
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
def sparql_to_documents(
    kg: Graph | SPARQLWrapper, graph: Optional[str] = None
) -> list[Document]:
    return list(akrdf.get_subjects_docs(kg, graph=graph))


@task
def index_batch(batch: list[Document]):
    """Sends a batch of document for indexing in the vector store"""
    coll.add(
        ids=[str(uuid.uuid4()) for _ in batch],
        documents=[doc.page_content for doc in batch],
        metadatas=[doc.metadata for doc in batch],
    )


@flow
def chroma_build_flow(
    chroma_cfg: ChromaConfig = ChromaConfig(),
    sparql_cfg: SparqlConfig = SparqlConfig(),
    graph: Optional[str] = None,
):
    """Build a ChromaDB vector index from RDF data in a SPARQL endpoint.

    Parameters
    ----------
    chroma_cfg:
        ChromaDB configuration.
    sparql_cfg:
        SPARQL endpoint configuration.
    graph:
        URI of named graph from which to select subjects to embed.
        By default, all subjects are used.
    """
    load_dotenv()
    logger = get_run_logger()
    logger.info("INFO Started")
    # Connect to external resources
    global coll
    client, coll = init_chromadb(
        chroma_cfg.host,
        chroma_cfg.port,
        chroma_cfg.collection_name,
        chroma_cfg.embedding_model,
        chroma_cfg.persist_directory,
    )
    kg = akrdf.setup_kg(
        sparql_cfg.endpoint,
        user=sparql_cfg.user,
        password=sparql_cfg.password,
    )

    # Create subject documents
    docs = sparql_to_documents(
        kg,
        graph=graph,
    )

    # Vectorize and index documents by batches to reduce overhead
    logger.info(f"Indexing by batches of {chroma_cfg.batch_size} items")
    embed_counter = 0
    for batch in chunked(docs, chroma_cfg.batch_size):
        embed_counter += len(batch)
        index_batch(batch)
    logger.info(f"Indexed {embed_counter} items.")


def cli(
    chroma_cfg_path: Annotated[
        Optional[Path],
        typer.Option(default=None, help="YAML file with Chroma client configuration."),
    ] = None,
    sparql_cfg_path: Annotated[
        Optional[Path],
        typer.Option(
            default=None, help="YAML file with SPARQL endpoint configuration."
        ),
    ] = None,
    graph: Annotated[
        Optional[str],
        typer.Option(
            default=None,
            help="URI of named graph from which to select triples to embed. If not set, the default graph is used.",
        ),
    ] = None,
):
    """Command line wrapper for RDF to ChromaDB index flow."""
    chroma_cfg = (
        parse_yaml_config(chroma_cfg_path, ChromaConfig)
        if chroma_cfg_path
        else ChromaConfig()
    )
    sparql_cfg = (
        parse_yaml_config(sparql_cfg_path, SparqlConfig)
        if sparql_cfg_path
        else SparqlConfig()
    )
    chroma_build_flow(chroma_cfg, sparql_cfg, graph=graph)


if __name__ == "__main__":
    typer.run(cli)
