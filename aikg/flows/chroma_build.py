"""This flow builds a ChromaDB vector index from RDF data.

The RDF data is split into "documents" consisting of triples with the same
subject. The documents are then vectorized using a language model and
stored in a vector (key-value) index. The index is persisted to disk and
can be subsequently loaded into memory for querying."""

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
from tqdm import tqdm
import typer

from aikg.config.chroma import Config, Location
from aikg.config.common import parse_yaml_config
from aikg.utils.chroma import get_chroma_client
import aikg.utils.rdf as akrdf


@task
def load_instances(instance_path: Path) -> Iterator[Graph]:
    """Lazy load the instances RDF graph(s) into one graph per instance."""

    instance_quads = ConjunctiveGraph()
    instance_quads.parse(instance_path)

    return akrdf.split_conjunctive_graph_by_subject(instance_quads)


@task
def load_schema(schema_path: Path) -> Graph:
    """Load source schema/ontology graph."""

    schema_graph = Graph()
    schema_graph.parse(schema_path)

    return schema_graph


@task
def init_chromadb(
    chroma_url: str, collection_name: str, embedding_model: str
) -> ChromaVectorStore:
    """Prepare chromadb client."""
    from chromadb.utils import embedding_functions

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model
    )
    chroma_client = get_chroma_client(chroma_url)
    try:
        chroma_client.delete_collection(collection_name)
    except HTTPError:
        pass
    collection = chroma_client.get_or_create_collection(
        collection_name, embedding_function=embedding_function
    )
    return ChromaVectorStore(chroma_collection=collection)


@task
def make_documents(schema_graph: Graph, instance_graphs: list[Graph]) -> list[Document]:
    """Build and documents from instance graphs."""

    loader = akrdf.CustomRDFReader()
    # Schema injected into each instance graph to provide human readable context
    import joblib

    doc_graphs = map(lambda g: g | schema_graph, instance_graphs)
    runner = joblib.Parallel(n_jobs=12)
    documents = runner(joblib.delayed(loader.load_data)(g) for g in doc_graphs)
    # Only non-empty documents are kept
    return [doc for doc in documents if doc.text]


@task
def sparql_to_documents(endpoint: str, user: str, password: str) -> list[Document]:
    return akrdf.split_documents_from_endpoint(endpoint, user, password)


def index_batch(batch: list[Document], chroma: ChromaVectorStore):
    """Sends a batch of document for indexing in the vector store"""
    chroma._collection.add(
        ids=[doc.doc_id for doc in batch],
        documents=[doc.text for doc in batch],
        metadatas=[doc.extra_info for doc in batch],
    )


@flow
def chroma_build_flow(location: Location, config: Config = Config()):
    """Build a ChromaDB vector index from RDF data."""
    load_dotenv()
    logger = get_run_logger()
    logger.info("INFO Started")
    chroma = init_chromadb(
        config.chroma_url, config.collection_name, config.embedding_model
    )

    # Load RDF data into documents. If available, use SPARQL endpoint
    if location.sparql_endpoint:
        docs = akrdf.split_documents_from_endpoint(
            location.sparql_endpoint,
            location.sparql_user,
            location.sparql_password,
        )
        docs = list(docs)
    # Otherwise load from RDF file using rdflib (much slower)
    else:
        schema = load_schema(location.schema_path)
        instances = load_instances(location.instances_path)
        docs = make_documents(schema, instances)

    # Vectorize and index documents by batches to reduce overhead
    logger.info(f"Indexing by batches of {config.batch_size} instances")
    for batch in chunked(docs, config.batch_size):
        index_batch(batch, chroma)


def cli(
    location_file: Annotated[
        Path,
        typer.Argument(help="YAML file with location of RDF data to index"),
    ],
    config_file: Annotated[
        Optional[Path],
        typer.Argument(help="YAML file with Chroma client configuration."),
    ] = None,
):
    """Command line wrapper for RDF to ChromaDB index flow."""
    location = parse_yaml_config(location_file, Location)
    config = parse_yaml_config(config_file, Config) if config_file else Config()
    chroma_build_flow(location, config)


if __name__ == "__main__":
    typer.run(cli)
