import re
from pathlib import Path
from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from metaflow import FlowSpec, IncludeFile, step, Parameter

from aikg.utils.io import download_file

QUESTION = "What is the tallest Pokemon?"


class PromptFlow(FlowSpec):
    question = Parameter(
        "question",
        default="What is the tallest Pokemon?",
        help="Question to answer",
        type=str,
        required=True,
    )
    config = IncludeFile(
        "config",
        default="aikg/config/base.yaml",
        help="YAML config file",
        required=True,
    )

    @step
    def start(self):
        import yaml

        config = yaml.safe_load(self.config)
        self.model_url = config["model_url"]
        self.model_path = Path(config["model_path"])
        self.prompt_template = config["prompt_template"]

        self.next(self.download_model)

    @step
    def download_model(self):
        if not self.model_path.exists():
            download_file(self.model_url, self.model_path)
        self.next(self.setup_llm)

    @step
    def setup_llm(self):
        # Detect input {variables} from template
        variables = re.findall(r"{(\w+)}", self.prompt_template)
        prompt = PromptTemplate(
            template=self.prompt_template, input_variables=variables
        )

        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        # Verbose is required to pass to the callback manager
        llm = GPT4All(
            model=self.model_path, callback_manager=callback_manager, verbose=True
        )
        self.llm_chain = LLMChain(prompt=prompt, llm=llm)
        self.next(self.ask_question)

    @step
    def ask_question(self):
        self.llm_chain.run(self.question)
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    PromptFlow()
