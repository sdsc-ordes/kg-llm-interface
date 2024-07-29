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

import requests
from pathlib import Path
from typing import TextIO
from langchain.schema import Document
from tqdm import tqdm


def download_file(url: str, output_path: str | Path):
    # send a GET request to the URL to download the file. Stream since it's large
    response = requests.get(url, stream=True)

    # open the file in binary mode and write the contents of the response to it in chunks
    # This is a large file, so be prepared to wait.
    with open(output_path, "wb") as f:
        for chunk in tqdm(response.iter_content(chunk_size=8192)):
            if chunk:
                f.write(chunk)


def parse_sparql_example(example: TextIO) -> Document:
    """
    Parse a text stream as input with first line being a question (starting with #)
    and the remaining lines being a (SPARQL) query. We reformat this content into a document
    where the page content is the question and the query is attached as metadata
    """
    # Create temp variable to process text stream
    example_temp = []
    example_temp.append(example.read())
    # Splitting the file content into lines
    lines = example_temp[0].split("\n")
    # Extracting the question (removing '#' from the first line)
    question = lines[0].strip()[1:]
    # Extracting the SPARQL query from the remaining lines
    sparql_query = "\n".join(lines[1:])
    # Create example document for the output
    example_doc = Document(page_content=question, metadata={"query": sparql_query})
    return example_doc
