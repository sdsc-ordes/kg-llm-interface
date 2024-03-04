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

"""This flow populates a SPARQL endpoint from RDF data in a file."""
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

from dotenv import load_dotenv
from prefect import flow, get_run_logger, task
from SPARQLWrapper import SPARQLWrapper
import typer

from aikg.config.common import parse_yaml_config
from aikg.config import SparqlConfig


@task
def setup_sparql_endpoint(
    endpoint: str, user: Optional[str] = None, password: Optional[str] = None
) -> SPARQLWrapper:
    """Connect to SPARQL endpoint and setup credentials.

    Parameters
    ----------
    endpoint:
        URL of the SPARQL endpoint.
    user:
        Username to use for authentication.
    password:
        Password to use for authentication.
    """
    # Setup sparql endpoint
    sparql = SPARQLWrapper(endpoint, updateEndpoint=endpoint + "/statements")
    if user and password:
        sparql.setCredentials(user, password)
    return sparql


@task
def insert_triples(
    rdf_file: Path, endpoint: SPARQLWrapper, graph: Optional[str] = None
):
    """Insert triples from source file into SPARQL endpoint.

    Parameters
    ----------
    rdf_file:
        Path to RDF file to load into the SPARQL endpoint.
    endpoint:
        SPARQL endpoint to load RDF data into.
    graph:
        URI of named graph to load RDF data into.
        If set to None, the default graph is used.
    """
    from rdflib import Dataset

    data = Dataset()
    data.parse(rdf_file)

    query = "\n".join(
        [f"PREFIX {prefix}: {ns.n3()}" for prefix, ns in data.namespaces()]
    )
    query += f"\nINSERT DATA {{"
    if graph:
        query += f"\n\tGRAPH <{graph}> {{"
    query += " .\n".join(
        [f"\t\t{s.n3()} {p.n3()} {o.n3()}" for (s, p, o, _) in data.quads()]
    )
    if graph:
        query += f"\n\t}}"
    query += f" . \n\n}}\n"
    endpoint.setQuery(query)
    endpoint.queryType = "INSERT"
    endpoint.method = "POST"
    endpoint.setReturnFormat("json")
    endpoint.query()


@flow
def sparql_insert_flow(
    rdf_file: Path,
    sparql_cfg: SparqlConfig = SparqlConfig(),
    graph: Optional[str] = None,
):
    """Workflow to connect to a SPARQL endpoint and send insert
    queries to load triples from a local file.

    Parameters
    ----------
    rdf_file:
        Path to source RDF file.
    sparql_cfg:
        Configuration for the target SPARQL endpoint.
    """
    load_dotenv()
    logger = get_run_logger()
    sparql = setup_sparql_endpoint(
        sparql_cfg.endpoint, sparql_cfg.user, sparql_cfg.password
    )
    logger.info("INFO SPARQL endpoint connected")
    insert_triples(rdf_file, sparql, graph)


def cli(
    rdf_file: Annotated[
        Path,
        typer.Argument(
            help="RDF file to load into the SPARQL endpoint, in turtle or n-triples format.",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
    sparql_cfg_path: Annotated[
        Optional[Path],
        typer.Option(help="YAML file with SPARQL endpoint configuration."),
    ] = None,
    graph: Annotated[
        Optional[str],
        typer.Option(
            help="URI of named graph to load RDF data into. If not set, the default graph is used.",
        ),
    ] = None,
):
    """Command line wrapper to insert triples to a SPARQL endpoint."""
    sparql_cfg = (
        parse_yaml_config(sparql_cfg_path, SparqlConfig)
        if sparql_cfg_path
        else SparqlConfig()
    )
    sparql_insert_flow(rdf_file, sparql_cfg, graph)


if __name__ == "__main__":
    typer.run(cli)
