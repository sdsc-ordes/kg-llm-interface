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

"""This is the chat server. It receives JSON messages with a question,
fetches context for that question in a vector store and injects them into a prompt.
It then sends the prompt to a LLM and returns the response to the client.
"""
from datetime import datetime
import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.llms import OpenAI
from pathlib import Path

from aikg.config import ChatConfig, ChromaConfig, SparqlConfig
from aikg.config.common import parse_yaml_config
from aikg.models import Conversation, Message
from aikg.utils.chat import generate_answer, generate_examples, generate_sparql
from aikg.utils.llm import setup_llm_chain
from aikg.utils.chroma import setup_collection, setup_client
from aikg.utils.rdf import setup_kg, query_kg

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

load_dotenv()
chroma_config = ChromaConfig()
sparql_config = SparqlConfig()
if os.environ.get("CHAT_CONFIG"):
    chat_config = parse_yaml_config(Path(os.environ["CHAT_CONFIG"]), ChatConfig)
else:
    chat_config = ChatConfig()


client = setup_client(
    chroma_config.host,
    chroma_config.port,
    chroma_config.persist_directory,
)
collection = setup_collection(
    client,
    chroma_config.collection_name,
    chroma_config.embedding_model,
)

llm = OpenAI(
    model_name="gpt-3.5-turbo-instruct",
    api_key=chat_config.openai_api_key,
    base_url=chat_config.openai_url,
)

answer_chain = setup_llm_chain(llm, chat_config.answer_template)
sparql_chain = setup_llm_chain(llm, chat_config.sparql_template)
kg = setup_kg(**sparql_config.dict())
app = FastAPI()


@app.get("/")
def index():
    return {
        "title": "Hello, welcome to the knowledge graph chatbot!",
        "description": "This is a simple chatbot that uses a knowledge graph to answer questions.",
        "usage": "Ask a single question using /ask?question='...', or only generate the query using /sparql?question='...'.",
    }


@app.get("/test/")
async def test() -> Message:
    return Message(text="Hello, world!", sender="AI", time=datetime.now())


@app.get("/ask/")
async def ask(question: str) -> Message:
    """Generate sparql query from question
    and execute query on kg and return an answer based on results."""
    ...
    query = generate_sparql(question, collection, sparql_chain)
    results = query_kg(kg, query)
    answer = generate_answer(question, query, results, answer_chain)
    return Message(text=answer, sender="AI", time=datetime.now())


@app.get("/sparql/")
async def sparql(question: str) -> Message:
    """Generate and return sparql query from question."""
    query = generate_sparql(question, collection, sparql_chain)
    return Message(text=query, sender="AI", time=datetime.now())
