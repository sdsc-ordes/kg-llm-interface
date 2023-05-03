from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Optional


class Location(BaseModel):
    ...


class Config(BaseModel):
    chat_model_id: str = "chainyo/alpaca-lora-7b"
    max_new_tokens: int = 256
    max_input_size: int = 2048
    num_output: int = 256
    max_chunk_overlap: int = 20

    prompt_template: str = (
        "We have provided the contextual facts below in the form of "
        "<subject> <predicate> <object> triples.\n"
        "-----------------\n"
        "{context_str}\n"
        "-----------------\n"
        "Please answer the question using only the context and no "
        "prior knowledge. If the context is insufficient to answer "
        "the question, simply answer the words 'Not found'.\n"
        "Question: {query_str}"
    )
