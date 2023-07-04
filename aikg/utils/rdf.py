from itertools import groupby
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from rdflib import ConjunctiveGraph, Graph
from rdflib.namespace import RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, CSV


RDF_DOC_QUERY = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?s ?p ?o ?sLab ?pLab ?oClean
WHERE
{{
    ?s ?p ?o .
    ?s rdfs:label ?sLab .
    ?p rdfs:label ?pLab .
    OPTIONAL {{
        ?o rdfs:label ?oLab .
        FILTER(LANG(?oLab) = "{lang}")
    }}
    BIND(COALESCE(?oLab, ?o) AS ?oLabOrUri)
    BIND(
        IF (isLiteral(?o), ?o, STR(?oLabOrUri))
        AS ?oLabOrVal
    )
    FILTER(LANG(?sLab) = "{lang}")
    FILTER(LANG(?pLab) = "{lang}")
    FILTER(LANG(?oLabOrVal) = "{lang}" || LANG(?oLabOrVal) = "")
    BIND (REPLACE(STR(?oLabOrVal), "^.*[#/:]([^/:#]*)$", "$1") as ?oClean)
    {graph_mask}
}}
"""


def split_graph_by_subject(graph: Graph) -> Iterator[Graph]:
    """Generate RDF documents (triples) by splitting input graph.
    Each document contains all triples with the same subject."""

    subjects = set(graph.subjects())
    for subject in subjects:
        # Create a new graph for each subject
        new_graph = Graph()
        new_graph += graph.triples((subject, None, None))
        # Yield the new graph
        yield new_graph


def split_conjunctive_graph_by_subject(graph: ConjunctiveGraph) -> Iterator[Graph]:
    """Generate RDF documents (triples) by splitting input graph.
    Each document contains all triples with the same subject."""
    for ctx in graph.contexts():
        for subject_graph in split_graph_by_subject(ctx):
            yield subject_graph


def split_documents_from_endpoint(
    endpoint: str,
    user: Optional[str] = None,
    password: Optional[str] = None,
    graph: Optional[str] = None,
) -> Iterator[Document]:
    """Load subject-based documents from a SPARQL endpoint.

    Parameters
    ----------
    endpoint:
        URL of the SPARQL endpoint.
    user:
        Username to use for authentication.
    password:
        Password to use for authentication.
    graph:
        URI of named graph to load RDF data from.
        If not specified, all subjects are used.
    """

    if graph:
        graph_mask = f"FILTER EXISTS {{ GRAPH {graph} {{ ?s ?p ?o }} }}"
    else:
        graph_mask = ""

    # Setup sparql endpoint
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(CSV)
    if user and password:
        sparql.setCredentials(user, password)
    sparql.setQuery(RDF_DOC_QUERY.format(lang="en", graph_mask=graph_mask)))

    # Load the query results
    # Query results contain 6 columns:
    # subject, predicate, object, subject label, predicate label, object label
    results = sparql.queryAndConvert().decode("utf-8").split("\r\n")
    # Parse csv fields
    results = map(lambda x: x.split(",", maxsplit=5), results)
    # Exclude empty / incomplete results (e.g. missing labels)
    results = filter(lambda x: len(x) == 6, results)
    next(results)  # skip header
    results = sorted(results, key=lambda x: x[0])[1:]
    # Yield triples and text by subject
    for k, g in groupby(results, lambda x: x[0]):
        # Original triples about subject k
        data = list(g)
        triples = "\n".join([f"<{s}> <{p}> <{o}>" for s, p, o, sl, pl, ol in data])
        # Human-readable "triples" about subject k
        doc = "\n".join([" ".join(elem[3:]) for elem in data])
        yield Document(doc, extra_info={"subject": k, "triples": triples})


class CustomRDFReader(BaseReader):
    """RDF reader."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize loader."""
        super().__init__(*args, **kwargs)

        self.g_global = Graph()
        self.g_global.parse(str(RDF))
        self.g_global.parse(str(RDFS))

    def load_data(
        self, graph: Path | Graph, extra_info: Optional[Dict] = None
    ) -> Document:
        """Parse graph into a document of human-readable triples. All
        URIs are converted to their rdfs:label when possible. Objects
        URIs without labels are converted to their fragment. Literals
        are kept as they are.

        Parameters
        ---------
        graph:
            Path to the graph file or the graph itself.
        extra_info:
            Extra information to be stored in the document.
            The "lang" key is used to specify the language of the document.
        """
        if extra_info is None:
            extra_info = {"lang": "en"}
        lang = extra_info.get("lang", "en")

        if isinstance(graph, Graph):
            g_local = graph
        else:
            g_local = Graph()
            g_local.parse(graph)

        res = (g_local | self.g_global).query(RDF_DOC_QUERY.format(lang=lang))

        # human-readable labels stored as document text
        text = "\n".join([f"{s} {p} {o}" for (_, _, _, s, p, o) in res])
        # original triples stored as extra info
        extra_info["triples"] = "\n".join(
            [f"<{s}> <{p}> <{o}>" for (s, p, o, _, _, _) in res]
        )

        return Document(text, extra_info=extra_info)
