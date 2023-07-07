from aikg.config import ChromaConfig, SparqlConfig
from aikg.flows.chroma_build import chroma_build_flow
from aikg.flows.insert_triples import sparql_insert_flow


def test_init_data(schema_file, small_instance_file):
    sparql_insert_flow(schema_file, SparqlConfig())
    sparql_insert_flow(small_instance_file, SparqlConfig())
    chroma_build_flow()
