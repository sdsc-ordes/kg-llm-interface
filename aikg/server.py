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
from pathlib import Path
from rdflib import Graph

from aikg.config import ChatConfig, ChromaConfig, SparqlConfig
from aikg.config.common import parse_yaml_config
from aikg.models import Conversation, Message
from aikg.utils.chat import post_process_answer, generate_sparql
from aikg.utils.llm import setup_llm_chain, setup_llm
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
llm = setup_llm(chat_config.model_id, chat_config.max_new_tokens)
# For now, both chains share the same model to spare memory
answer_chain = setup_llm_chain(llm, chat_config.answer_template)
sparql_chain = setup_llm_chain(llm, chat_config.sparql_template)
kg = setup_kg(**sparql_config.dict())
app = FastAPI()


@app.get("/")
def index():
    return {
        "title": "Hello, welcome to the knowledge graph chatbot!",
        "description": "This is a simple chatbot that uses a knowledge graph to answer questions.",
        "usage": "Ask a single question using /ask?question='...', or POST a Conversation object to /chat.",
    }


@app.post("/chat")
async def chat(conversation: Conversation) -> Conversation:
    # question = conversation.thread[-1].text
    # answer = ...
    # conversation.thread.append(answer)
    # return conversation
    ...


@app.get("/ask/")
async def test(question: str) -> Message:
    return Message(text="Hello, world!", sender="AI", time=datetime.now())


@app.get("/sparql/")
async def sparql(question: str) -> Message:
    """TODO: Generate sparql query from question
    and execute sparql query on kg."""
    ...
    query = generate_sparql(question, collection, sparql_chain)
    results = query_kg(kg, query)
    return Message(text=str(results), sender="AI", time=datetime.now())
    # answer = llm_chain.run(query_str=query, context_str=context)
    # answer = post_process_answer(answer)
    # return Message(text=answer, sender="AI", time=datetime.now())
