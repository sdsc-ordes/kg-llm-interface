from typing import Any, List, Mapping, Optional

from langchain.llms.base import LLM
import torch
from transformers import pipeline
from aikg.config import config


class CustomLLM(LLM):
    model_name = config["base"]["model_id"]
    pipeline = pipeline(
        "text-generation",
        model=model_name,
        model_kwargs={"torch_dtype": torch.bfloat16},
    )
    max_new_tokens = config["base"]["max_new_tokens"]

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        prompt_length = len(prompt)
        response = self.pipeline(prompt, max_new_tokens=self.max_new_tokens)[0][
            "generated_text"
        ]

        # only return newly generated tokens
        return response[prompt_length:]

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "custom"
