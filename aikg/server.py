"""This is the chat server. It receives JSON messages with a question,
fetches context for that question in a vector store and injects them into a prompt.
It then sends the prompt to a LLM and returns the response to the client.
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from llama_index import QuestionAnswerPrompt, GPTVectorStoreIndex, StorageContext

import aikg.config.chroma
import aikg.config.chat
from aikg.models import Conversation
from aikg.utils.chroma import connect_vector_store

import aikg.utils.llm as akllm

load_dotenv()
chroma_config = aikg.config.chroma.Config()
chat_config = aikg.config.chat.Config()


def setup_query_engine(
    index: GPTVectorStoreIndex, prompt_template: str, similarity_top_k: int = 2
):
    qa_prompt = QuestionAnswerPrompt(prompt_template)
    return index.as_query_engine(
        text_qa_template=qa_prompt, similarity_top_k=similarity_top_k
    )


def setup_chatbot():
    """Setup the prompt system, vector database and llm for the chatbot."""
    from llama_index.readers.chroma import ChromaReader

    vector_store = connect_vector_store(
        chroma_config.chroma_url, chroma_config.collection_name
    )
    ChromaReader(
        collection_name=chroma_config.collection_name,
        host=chroma_config.chroma_url,
        port=chroma_config.chroma_port,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = akllm.load_llm_context(chat_config)
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
    return {
        "title": "Hello, welcome to the knowledge graph chatbot!",
        "description": "This is a simple chatbot that uses a knowledge graph to answer questions.",
        "usage": "Ask a single question using /ask?question='...', or POST a Conversation object to /chat.",
    }


@app.post("/chat")
async def chat(conversation: Conversation) -> Conversation:
    question = conversation.last_message
    answer = process_question(question, chatbot)
    conversation.thread += question
    conversation.last_message = answer
    return conversation


@app.get("/ask/")
async def test(question: str):
    return process_question(question, chatbot)
