"""This is the chat server. It receives JSON messages with a question,
fetches context for that question in a vector store and injects them into a prompt.
It then sends the prompt to a LLM and returns the response to the client.
"""
from datetime import datetime
import logging
import os
import sys

from chromadb.api import Collection
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain import LLMChain
from rdflib import Graph

import aikg.config.chroma
import aikg.config.chat
import aikg.config.sparql
from aikg.models import Conversation, Message
from aikg.utils.chat import post_process_answer
from aikg.utils.llm import setup_llm_chain, setup_llm
from aikg.utils.chroma import setup_chroma
from aikg.utils.rdf import setup_kg, query_kg

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


load_dotenv()
chroma_config = aikg.config.chroma.ChromaConfig()
chat_config = aikg.config.chat.ChatConfig()
sparql_config = aikg.config.sparql.SparqlConfig()


def generate_sparql(
    question: str, collection: Collection, llm_chain: LLMChain, limit: int = 5
) -> str:
    """Retrieve k-nearest documents from the vector store and synthesize
    SPARQL query."""

    # Retrieve documents and triples from top k subjects
    results = collection.query(query_texts=question, n_results=limit)
    # Extract triples and concatenate as a ntriples string
    triples = "\n".join([res.get("triples", "") for res in results["metadatas"][0]])
    # Convert to turtle
    triples = Graph().parse(data=triples, format="nt").serialize(format="turtle")
    query = llm_chain.run(question_str=question, context_str=triples)
    return query


collection = setup_chroma(
    chroma_config.host,
    chroma_config.port,
    chroma_config.collection_name,
    chroma_config.embedding_model,
    chroma_config.persist_directory,
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
