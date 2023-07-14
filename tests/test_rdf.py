# Test RDF functionality to interact with a knowledge graph.
# The kg may be a SPARQL endpoint or a local RDF file.
from aikg.config import SparqlConfig
from aikg.utils.rdf import query_kg, setup_kg
import pytest

rdflib_config = SparqlConfig(
    endpoint="data/test_data.trig",
)
sparql_config = SparqlConfig(
    endpoint="https://sparql.uniprot.org/",
)

CONFIGS = [rdflib_config, sparql_config]
QUERIES = [
    "SELECT * WHERE { ?s ?p ?o } LIMIT 10",
    "DESCRIBE ?s WHERE { ?s ?p ?o } LIMIT 10",
]


@pytest.fixture
def sparql_kg():
    """A public SPARQL endpoint."""
    return setup_kg(sparql_config.endpoint, sparql_config.user, sparql_config.password)


@pytest.fixture
def rdflib_kg():
    """A local RDF file."""
    return setup_kg(rdflib_config.endpoint, rdflib_config.user, rdflib_config.password)


@pytest.mark.parametrize("kg", ["sparql_kg", "rdflib_kg"])
@pytest.mark.parametrize("query", QUERIES)
def test_run_query_kg(kg, query, request):
    """Test if a query on a kg returns at least one result."""
    res = query_kg(request.getfixturevalue(kg), query)
    assert len(res) >= 1


@pytest.mark.parametrize("query", QUERIES)
def test_compare_query_kg(sparql_kg, rdflib_kg, query):
    """Test if the same query on rdflib and sparql yields
    the same output dimensions."""
    rdflib_res = query_kg(rdflib_kg, query)
    sparql_res = query_kg(sparql_kg, query)
    assert len(sparql_res) == len(rdflib_res)
    assert all([len(x) == len(y) for x, y in zip(sparql_res, rdflib_res)])
