from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from rdflib import ConjunctiveGraph, Graph
from rdflib.namespace import RDF, RDFS


RDF_DOC_QUERY = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?sLab ?pLab ?oClean
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
        ----------
        graph:
            Path to the graph file or the graph itself.
        extra_info:
            Extra information to be stored in the document.
            The "lang" key is used to specify the language of the document.
        """

        lang = extra_info["lang"] if extra_info is not None else "en"

        if isinstance(graph, Graph):
            g_local = graph
        else:
            g_local = Graph()
            g_local.parse(graph)

        res = (g_local | self.g_global).query(RDF_DOC_QUERY.format(lang=lang))

        text = "\n".join([f"<{s}> <{p}> <{o}>" for (s, p, o) in res])

        return Document(text, extra_info=extra_info)
