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

import os
from pydantic import BaseModel


class ChatConfig(BaseModel):
    """Chatbot configuration.

    Attributes:
        model_id: The HuggingFace ID of the model to use for text generation.
        max_new_tokens: The maximum number of tokens to generate.
        max_input_size: The maximum number of tokens in the input.
        num_output: The number of outputs to generate.
        max_chunk_overlap: The maximum number of tokens to overlap between chunks.
        prompt_template: The template for the prompt to inject into the model. The template should contain the following variables: context_str, query_str.
    """

    openai_url: str = os.environ.get("OPENAI_URL", "https://api.openai.com/v1/")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    model: str = os.environ.get("OPENAI_MODEL", "gpt-4o")
    answer_template: str = """
We have provided the contextual facts below.
-----------------
{result_str}
-----------------
Answer the question using only the context and no
prior knowledge. If the context does not contain any fact related to
the question, simply answer the words 'Not found'. The answer should be
maximum 2 sentences directly reflecting the facts from relevant facts while ignoring
irrelevant ones.
Question: {question_str}
Answer:
    """

    sparql_template: str = """
Use the question and the additional information to generate a sparql query against a knowledge graph where the p and q items are
completely unknown to you. You will need to discover the p and q items before you can generate the sparql.
Do not assume you know the p and q items for any concepts.
After you generate the sparql, you should display it.

When generating sparql:
* Never enclose the sparql in back-quotes
* Do not include any human text, only the query and nothing else

{examples_str}

Use the following format:

Question: the input question for which you must provide a natural language answer
Information: the additional information you get with the query, in RDF format. This will help you generate the sparql query with the correct format.

Question: {question_str}
Information:
{context_str}
Answer:
"""
