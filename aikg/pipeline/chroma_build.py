"""This flow builds a ChromaDB vector index from RDF data.

The RDF data is split into "documents" consisting of triples with the same
subject. The documents are then vectorized using a language model and
stored in a vector (key-value) index. The index is persisted to disk and
can be subsequently loaded into memory for querying."""

import re
from dotenv import load_dotenv
from pathlib import Path
from metaflow import conda_base, FlowSpec, IncludeFile, Parameter, step

from aikg.config import config
import aikg.utils.rdf as akrdf


class ChromaBuildFlow(FlowSpec):
    instance_path = Parameter(
        "instance_path",
        help="The path to instance graph(s) to index. URL or RDF file.",
        type=str,
        required=True,
    )
    schema_path = Parameter(
        "schema_path",
        help="The path to the schema graph. URL or RDF file.",
        type=str,
        required=True,
    )
    collection_name = Parameter(
        "collection_name",
        help="The name of the ChromaDB collection to store the index in.",
        default="test",
        type=str,
    )
    chroma_url = Parameter(
        "chroma_url",
        help="The URL of the ChromaDB server.",
        default="http://localhost:8000",
        type=str,
    )

    @step
    def start(self):
        """Initialize config values"""
        import yaml

        self.config = config

        self.next(self.load_instances)

    @step
    def load_instances(self):
        """Load the instances RDF graph(s) into one graph per instance."""
        from rdflib import ConjunctiveGraph

        instance_quads = ConjunctiveGraph()
        instance_quads.parse(self.instance_path)
        self.instance_graphs = [
            s for s in akrdf.split_conjunctive_graph_by_subject(instance_quads)
        ]
        self.next(self.load_schema)

    @step
    def load_schema(self):
        """Load source schema/ontology graph"""
        from rdflib import Graph

        self.schema_graph = Graph()
        self.schema_graph.parse(self.schema_path)
        self.next(self.init_chromadb)

    def load_embedding_model(self):
        """Load the language model used to compute embeddings."""
        from llama_index import LangchainEmbedding, ServiceContext
        from langchain.embeddings import HuggingFaceEmbeddings

        embed_model = LangchainEmbedding(HuggingFaceEmbeddings())
        self.service_context = ServiceContext.from_defaults(embed_model=embed_model)

    @step
    def init_chromadb(self):
        """Prepare chromadb client."""
        from requests import HTTPError
        import urllib.parse
        import chromadb
        from chromadb.config import Settings
        from llama_index.vector_stores import ChromaVectorStore

        # Connect to vector db server
        url = urllib.parse.urlsplit(self.chroma_url)
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
            chroma_client.delete_collection(self.collection_name)
        except HTTPError:
            pass
        collection = chroma_client.get_or_create_collection(self.collection_name)
        self.chroma = ChromaVectorStore(collection)
        self.next(self.batch_instances)

    @step
    def batch_instances(self):
        """Serve instance batches indexing."""
        from more_itertools import chunked

        # Instances will be indexed in batches to reduce overhead
        BATCH_SIZE = 100
        self.loader = akrdf.CustomRDFReader()
        # Schema injected into each instance graph to provide human readable context
        doc_graphs = map(lambda g: g | self.schema_graph, self.instance_graphs)
        self.doc_batches = list(chunked(doc_graphs, BATCH_SIZE))
        self.next(self.index_batch, foreach="doc_batches")

    @step
    def index_batch(self):
        """Index a batch of instances into the vector index."""
        self.gg = self.input
        # docs = [self.loader.load_data(inst) for inst in self.input if inst.text]
        # self.chroma.client.add(docs, ids=[doc.doc_id for doc in docs])
        self.next(self.save_graph)

    @step
    def save_graph(self, docs: None):
        print(f"I expect nothing: {docs}")
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    load_dotenv()
    ChromaBuildFlow()
