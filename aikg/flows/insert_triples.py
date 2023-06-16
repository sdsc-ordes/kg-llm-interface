"""This flow populates a SPARQL endpoint from RDF data in a file."""
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

from dotenv import load_dotenv
from prefect import flow, get_run_logger, task
from SPARQLWrapper import SPARQLWrapper
import typer

from aikg.config.common import parse_yaml_config
from aikg.config.sparql import SparqlConfig


@task
def setup_sparql_endpoint(
    endpoint: str, user: Optional[str] = None, password: Optional[str] = None
) -> SPARQLWrapper:
    # Setup sparql endpoint
    sparql = SPARQLWrapper(endpoint, updateEndpoint=endpoint + "/statements")
    if user and password:
        sparql.setCredentials(user, password)
    return sparql


@task
def insert_triples(rdf_file: Path, endpoint: SPARQLWrapper):
    """Sends a batch of document for indexing in the vector store"""
    from rdflib import Dataset

    data = Dataset()
    data.parse(rdf_file)
    
    query = "\n".join([f"PREFIX {prefix}: {ns.n3()}" for prefix, ns in data.namespaces()])
    query += f"\nINSERT DATA {{"
    query += " .\n".join(
        [
            f"\t\t{s.n3()} {p.n3()} {o.n3()}"
            for (s, p, o, _) in data.quads()
        ]
    )
    query += f" . \n\n}}\n"
    endpoint.setQuery(query)
    endpoint.queryType = "INSERT"
    endpoint.method = "POST"
    endpoint.setReturnFormat("json")
    results = endpoint.query()


@flow
def sparql_insert_flow(
    rdf_file: Path,
    sparql_cfg: SparqlConfig = SparqlConfig(),
):
    """Build a ChromaDB vector index from RDF data in a SPARQL endpoint."""
    load_dotenv()
    logger = get_run_logger()
    sparql = setup_sparql_endpoint(
        sparql_cfg.endpoint, sparql_cfg.user, sparql_cfg.password
    )
    logger.info("INFO SPARQL endpoint connected")
    insert_triples(rdf_file, sparql)


def cli(
    rdf_file: Annotated[
        Path,
        typer.Argument(
            help="RDF file to load into the SPARQL endpoint, in turtle or n-triples format."
        ),
    ],
    sparql_cfg_path: Annotated[
        Optional[Path],
        typer.Option(help="YAML file with SPARQL endpoint configuration."),
    ] = None,
):
    """Command line wrapper to insert triples to a SPARQL endpoint."""
    sparql_cfg = (
        parse_yaml_config(sparql_cfg_path, SparqlConfig)
        if sparql_cfg_path
        else SparqlConfig()
    )
    sparql_insert_flow(rdf_file, sparql_cfg)


if __name__ == "__main__":
    typer.run(cli)
