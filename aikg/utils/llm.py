from typing import Any, List, Mapping, Optional

from langchain.llms.base import LLM
import torch
from transformers import pipeline
from aikg.config import config

LLM_CONFIG = config["llm"]


class CustomLLM(LLM):
    model_id: str = LLM_CONFIG["model_id"]
    pipeline = pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
    )

    def _call(
        self, prompt: str, max_new_tokens: int = LLM_CONFIG["max_new_tokens"]
    ) -> str:
        prompt_length = len(prompt)
        response = self.pipeline(prompt, max_new_tokens=max_new_tokens)[0][
            "generated_text"
        ]

        # only return newly generated tokens
        return response[prompt_length:]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_id}

    @property
    def _llm_type(self) -> str:
        return "custom"
