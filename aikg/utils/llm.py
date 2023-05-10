from typing import Any, List, Mapping, Optional

from langchain.llms.base import LLM
from llama_index import LangchainEmbedding, PromptHelper
from llama_index import LLMPredictor, ServiceContext
import torch
from transformers import pipeline
import aikg.config.chat

LLM_CONFIG = aikg.config.chat.Config()


class CustomLLM(LLM):
    model_id: str = LLM_CONFIG.model_id
    pipeline = pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
    )

    def _call(
        self, prompt: str, max_new_tokens: int = LLM_CONFIG.max_new_tokens
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


def load_llm_context(config: aikg.config.chat.Config) -> ServiceContext:
    prompt_helper = PromptHelper(
        config.max_input_size, config.num_output, config.max_chunk_overlap
    )

    # define our LLM
    llm_predictor = LLMPredictor(llm=CustomLLM())

    return ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        prompt_helper=prompt_helper,
    )
