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

"""Utilities to help processing chatbot prompts or answers."""
from typing import Any, Iterable

from chromadb.api import Collection
from rdflib import Graph
from langchain import LLMChain


def keep_first_line(text: str) -> str:
    r"""Truncate a string to the first non-empty line.

    Examples
    --------
    >>> keep_first_line("\nFirst line.\nSecond line.")
    'First line.'
    """
    return text.lstrip("\n").split("\n")[0].strip(" ")


def drop_if_keyword(text: str, keyword: str = "Not found.") -> str:
    """If input keyword occurs in text, replace it with the keyword.

    Examples
    --------
    >>> drop_if_keyword("Not found. Some made up answer.", keyword="Not found.")
    'Not found.'
    """
    if keyword in text:
        return keyword
    return text


def post_process_answer(answer: str) -> str:
    """Post-process an answer by keeping only the first line and dropping
    it if it contains the keyword 'Not found.'."""
    text = keep_first_line(answer)
    text = drop_if_keyword(text)
    return text


def generate_sparql(
    question: str, collection: Collection, llm_chain: LLMChain, limit: int = 5
) -> str:
    """Retrieve k-nearest documents from the vector store and synthesize
    SPARQL query."""

    # Retrieve documents and triples from top k subjects
    results = collection.query(query_texts=question, n_results=limit)
    # Extract triples and concatenate as a ntriples string
    triples = "\n".join([res.get("triples", "") for res in results["metadatas"][0]])
    # Convert to turtle for better readability and fewer tokens
    triples = Graph().parse(data=triples).serialize(format="turtle")
    query = llm_chain.run(question_str=question, context_str=triples)
    return query


def generate_answer(
    question: str,
    query: str,
    results: Iterable[Any],
    llm_chain: LLMChain,
) -> str:
    """
    Given a question, associated SPARQL query and execution result,
    use a LLM to generate a natural language answer describing the results.
    """
    # Extract triples and concatenate as a ntriples string
    fmt_results = ["\n".join(map(str, results))]
    answer = llm_chain.run(
        query_str=query, question_str=question, result_str=fmt_results
    )
    return answer
