"""This is the chat server. It receives JSON messages with a question,
fetches context for that question in a vector store and injects them into a prompt.
It then sends the prompt to a LLM and returns the response to the client.
"""


import asyncio
import json
import logging
import urllib.parse


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index import LangchainEmbedding, PromptHelper
from llama_index import LLMPredictor, ServiceContext
from llama_index import QuestionAnswerPrompt, GPTVectorStoreIndex, StorageContext
from llama_index.vector_stores import ChromaVectorStore

import aikg.config.chroma
import aikg.config.chat
from aikg.config.common import parse_yaml_config
from aikg.utils.chroma import get_chroma_client
import aikg.utils.llm as akllm

chroma_config = aikg.config.chroma.Config()
chat_config = aikg.config.chat.Config()


def load_llm(config: aikg.config.chat.Config) -> ServiceContext:
    prompt_helper = PromptHelper(
        config.max_input_size, config.num_output, config.max_chunk_overlap
    )

    # define our LLM
    llm_predictor = LLMPredictor(llm=akllm.CustomLLM())

    return ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        prompt_helper=prompt_helper,
    )


def setup_query_engine(
    index: GPTVectorStoreIndex, prompt_template: str, similarity_top_k: int = 2
):
    qa_prompt = QuestionAnswerPrompt(prompt_template)
    return index.as_query_engine(
        text_qa_template=qa_prompt, similarity_top_k=similarity_top_k
    )


def connect_vector_store(url: str, collection: str) -> ChromaVectorStore:
    chroma_client = get_chroma_client(url)
    chroma_collection = chroma_client.get_or_create_collection(collection)
    return ChromaVectorStore(chroma_collection=chroma_collection)


def setup_chatbot():
    vector_store = connect_vector_store(
        chroma_config.chroma_url, chroma_config.collection_name
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = load_llm(chat_config)
    index = GPTVectorStoreIndex(
        storage_context=storage_context, service_context=service_context
    )
    query_engine = setup_query_engine(
        index,
        prompt_template=chat_config.prompt_template,
    )
    return query_engine


def process_question(question: str, query_engine) -> str:
    return query_engine.query(question)


chatbot = setup_chatbot()
app = FastAPI()


@app.get("/")
def index():
    return {"title": "Hello, welcome to the Gimie API"}


@app.post("/chat")
async def answer_question(question: str):
    answer = process_question(question, chatbot)
    return {"answer": answer}


@app.get("/chat/test/{question:path}")
async def test(question: str):
    ...
