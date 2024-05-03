import requests
import time

from testcontainers.core.container import DockerContainer
from aikg.config import ChromaConfig, SparqlConfig
from aikg.flows.chroma_build import chroma_build_flow
from aikg.flows.insert_triples import sparql_insert_flow

REPO_CONFIG = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix owlim: <http://www.ontotext.com/trree/owlim#> .

[] a rep:Repository ;
    rep:repositoryID "test" ;
    rdfs:label "test" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
            owlim:base-URL "http://www.ontotext.com/" ;
            # other configurations...
        ]
    ].
"""


def test_init_data(schema_file, small_instance_file):
    with (
        DockerContainer("ontotext/graphdb:10.2.2").with_bind_ports(7200, 7200)
    ) as graphdb:
        # container ready + margin for graphdb to start
        graphdb.get_exposed_port(7200)
        time.sleep(5)
        # Create test repo
        resp = requests.post(
            "http://localhost:7200/rest/repositories", files={"config": REPO_CONFIG}
        )
        sparql_insert_flow(schema_file, SparqlConfig())
        sparql_insert_flow(small_instance_file, SparqlConfig())
        chroma_build_flow(ChromaConfig(host="local"))
