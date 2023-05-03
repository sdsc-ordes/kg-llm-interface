"""This flow builds a ChromaDB vector index from RDF data.

The RDF data is split into "documents" consisting of triples with the same
subject. The documents are then vectorized using a language model and
stored in a vector (key-value) index. The index is persisted to disk and
can be subsequently loaded into memory for querying."""

from pathlib import Path
import sys
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
from rdflib import ConjunctiveGraph, Graph
from requests import HTTPError
import typer

from aikg.config.chroma import Config, Location
from aikg.config.common import parse_yaml_config
import aikg.utils.rdf as akrdf


@task
def load_instance_graphs(instance_path: Path) -> Iterator[Graph]:
    """Load the instances RDF graph(s) into one graph per instance."""

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
def init_chromadb(chroma_url: str, collection_name: str) -> ChromaVectorStore:
    """Prepare chromadb client."""

    # Connect to vector db server
    url = urllib.parse.urlsplit(chroma_url)
    chroma_host, chroma_port = (url.hostname, url.port)
    chroma_client = chromadb.Client(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host=chroma_host,
            chroma_server_http_port=chroma_port,
            anonymized_telemetry=False,
        )
    )
    try:
        chroma_client.delete_collection(collection_name)
    except HTTPError:
        pass
    collection = chroma_client.get_or_create_collection(collection_name)
    return ChromaVectorStore(collection)


@task
def batch_instances(
    schema_graph: Graph, instance_graphs: Iterator[Graph], batch_size: int = 500
):
    """Lazily serve instance batches for indexing."""

    # Instances will be indexed in batches to reduce overhead
    loader = akrdf.CustomRDFReader()
    # Schema injected into each instance graph to provide human readable context
    all_docs = map(lambda g: loader.load_data(g | schema_graph), instance_graphs)
    docs = filter(lambda d: d.text, all_docs)
    return chunked(docs, batch_size)


@task
def index_batch(batch: list[Document], chroma: ChromaVectorStore):
    """Index a batch of instances into the vector index."""
    chroma.client.add(ids=[doc.doc_id for doc in batch], documents=batch)


@flow
def chroma_build_flow(location: Location, config: Config = Config()):
    """Build a ChromaDB vector index from RDF data."""
    instances = load_instance_graphs(location.instances_path)
    schema = load_schema(location.schema_path)
    chroma = init_chromadb(config.chroma_url, config.collection_name)
    for batch in batch_instances(schema, instances):
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
    """Build a ChromaDB vector index from RDF data."""
    load_dotenv()
    location = parse_yaml_config(location_file, Location)
    config = parse_yaml_config(config_file, Config) if config_file else Config()
    chroma_build_flow(location, config)


if __name__ == "__main__":
    typer.run(cli)
