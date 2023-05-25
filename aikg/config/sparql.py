import os
from pydantic import BaseModel


class SparqlConfig(BaseModel):
    """
    Attributes:
        host: The host of the SPARQL endpoint.
        port: The port of the SPARQL endpoint.
        repo: The name of the repository or dataset to query.
        user: The username to use for authentication.
        password: The password to use for authentication.
    """

    endpoint: str = os.environ.get(
        "SPARQL_ENDPOINT", "http://localhost:7200/repositories/test"
    )
    user: str = os.environ.get("SPARQL_USER", "admin")
    password: str = os.environ.get("SPARQL_PASSWORD", "admin")
