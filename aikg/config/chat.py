from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Optional


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

    model_id: str = "chainyo/alpaca-lora-7b"
    max_new_tokens: int = 48
    max_input_size: int = 2048
    num_output: int = 256
    max_chunk_overlap: int = 20

    prompt_template: str = (
        "We have provided the contextual facts below.\n"
        "-----------------\n"
        "{context_str}\n"
        "-----------------\n"
        "Answer the question using only the context and no "
        "prior knowledge. If the context does not contain any fact related to "
        "the question, simply answer the words 'Not found'. The answer should be "
        "maximum 2 sentences directly reflecting the facts from relevant facts while ignoring "
        "irrelevant ones.\n"
        "Question: {query_str}"
        "Answer: "
    )
