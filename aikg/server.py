"""This is the chat server. It receives JSON messages with a question,
fetches context for that question in a vector store and injects them into a prompt.
It then sends the prompt to a LLM and returns the response to the client.
"""

import urllib.parse

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain import HuggingFacePipeline, LLMChain, PromptTemplate
from llama_index import QuestionAnswerPrompt, GPTVectorStoreIndex
from llama_index.readers.chroma import ChromaReader
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

import aikg.config.chroma
import aikg.config.chat
from aikg.models import Conversation

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


def setup_llm_chain() -> LLMChain:
    """Prepare the prompt injection and text generation system."""

    prompt = PromptTemplate(
        template=chat_config.prompt_template,
        input_variables=["context_str", "query_str"],
    )
    tok = AutoTokenizer.from_pretrained(chat_config.model_id)
    model = AutoModelForCausalLM.from_pretrained(chat_config.model_id)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tok,
        max_new_tokens=chat_config.max_new_tokens,
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return LLMChain(prompt=prompt, llm=llm)


def setup_chroma() -> ChromaReader:
    """Setup the connection to ChromaDB."""

    url = urllib.parse.urlsplit(chroma_config.chroma_url)
    chroma_host, chroma_port = (url.hostname, url.port)
    reader = ChromaReader(
        collection_name=chroma_config.collection_name,
        host=chroma_host,
        port=chroma_port,
    )
    return reader


def synthesize(query, reader, llm_chain, limit=5) -> str:
    """Retrieve k-nearest documents from the vector store and synthesize
    an answer using documents as context."""
    documents = reader.load_data(query=query, limit=limit)
    context = "\n".join([doc.text for doc in documents])
    answer = llm_chain.run(query_str=query, context_str=context)
    return answer


reader = setup_chroma()
llm_chain = setup_llm_chain()
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
    answer = synthesize(
        question,
        reader,
        llm_chain,
    )
    conversation.thread += question
    conversation.last_message = answer
    return conversation


@app.get("/ask/")
async def test(question: str):
    answer = synthesize(
        question,
        reader,
        llm_chain,
    )
    return answer
