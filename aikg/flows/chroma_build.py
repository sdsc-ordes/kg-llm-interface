"""This flow builds a ChromaDB vector index from RDF data in a SPARQL endpoint.

For each subject in the target graph, a document is generated. The document consists of:
* A human readable body made up of the annotations (rdfs:comment, rdf:label) associated with the subject.
* Triples with the subject attached as metadata.

The documents are then stored in a vector database. The embedding is computed using the document body,
and triples included as metadata. The index is persisted to disk and can be subsequently loaded into memory
for querying."""

from pathlib import Path
from typing import Iterator, Optional
from typing_extensions import Annotated
import urllib.parse

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from llama_index.vector_stores import ChromaVectorStore
from llama_index import Document
from more_itertools import chunked
from prefect import flow, task
from prefect import get_run_logger, unmapped
from prefect_dask.task_runners import DaskTaskRunner
from rdflib import ConjunctiveGraph, Graph
from requests import HTTPError
from SPARQLWrapper import SPARQLWrapper
from tqdm import tqdm
import typer

from aikg.config.chroma import ChromaConfig
from aikg.config.sparql import SparqlConfig
from aikg.config.common import parse_yaml_config
from aikg.utils.chroma import get_chroma_client
import aikg.utils.rdf as akrdf
from aikg.utils.chroma import setup_chroma


@task
def init_chromadb(
    host: str, port: int, collection_name: str, embedding_model: str
) -> ChromaVectorStore:
    """Prepare chromadb client."""
    collection = setup_chroma(host, port, collection_name, embedding_model)

    return ChromaVectorStore(chroma_collection=collection)


@task
def sparql_to_documents(
    kg: Graph | SPARQLWrapper, graph: Optional[str] = None
) -> list[Document]:
    return list(akrdf.split_documents_from_endpoint(kg, graph=graph))


@task
def index_batch(batch: list[Document], chroma: ChromaVectorStore):
    """Sends a batch of document for indexing in the vector store"""
    chroma._collection.add(
        ids=[doc.doc_id for doc in batch],
        documents=[doc.text for doc in batch],
        metadatas=[doc.extra_info for doc in batch],
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
    chroma = init_chromadb(**chroma_cfg.dict())
    kg = akrdf.setup_kg(**sparql_cfg.dict())

    # Create subject documents
    docs = sparql_to_documents(
        kg,
        graph=graph,
    )

    # Vectorize and index documents by batches to reduce overhead
    logger.info(f"Indexing by batches of {chroma_cfg.batch_size} instances")
    for batch in chunked(docs, chroma_cfg.batch_size):
        index_batch(batch, chroma)


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
