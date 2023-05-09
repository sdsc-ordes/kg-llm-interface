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
from llama_index import QuestionAnswerPrompt

from aikg.config.common import parse_yaml_config
from aikg.config.chroma import Config, Location
from aikg.utils.chroma import get_chroma_vectorstore
import aikg.utils.llm as akllm


def make_llm():
    # define prompt helper
    # set maximum input size
    max_input_size = 2048
    # set number of output tokens
    num_output = 256
    # set maximum chunk overlap
    max_chunk_overlap = 20

    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    # define our LLM
    llm_predictor = LLMPredictor(llm=akllm.CustomLLM())
    embed_model = LangchainEmbedding(HuggingFaceEmbeddings())

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        prompt_helper=prompt_helper,
        embed_model=embed_model,
    )
    index = get_chroma_vectorstore(chroma_url, collection)


def setup_prompt_helper():
    ...


def get_config() -> Config:
    ...


def process_question(question: str) -> str:
    ...
