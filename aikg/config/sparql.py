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

    host: str = os.environ.get("SPARQL_HOST", "http://localhost")
    port: int = int(os.environ.get("SPARQL_PORT", "7200"))
    repo: str = os.environ.get("SPARQL_REPO", "test")
    user: str = os.environ.get("SPARQL_USER", "admin")
    password: str = os.environ.get("SPARQL_PASSWORD", "admin")

    @property
    def endpoint(self):
        return f"{self.host}:{self.port}/{self.repo}"
