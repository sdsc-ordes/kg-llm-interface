import re
from dotenv import load_dotenv
from pathlib import Path
from metaflow import conda_base, FlowSpec, IncludeFile, Parameter, step


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
        """Initialize config values"""
        import yaml

        config = yaml.safe_load(self.config)
        self.model_id = config["model_id"]
        self.prompt_template = config["prompt_template"]

        self.next(self.make_prompt)

    @step
    def make_prompt(self):
        """Make the prompt template"""
        from langchain import PromptTemplate

        # Detect input {variables} from template
        variables = re.findall(r"{(\w+)}", self.prompt_template)
        self.prompt = PromptTemplate(
            template=self.prompt_template, input_variables=variables
        )
        self.next(self.setup_llm)

    @step
    def setup_llm(self):
        """Instantiate the LLM."""
        from langchain import HuggingFacePipeline, LLMChain
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

        # Verbose is required to pass to the callback manager
        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        print("Loaded: Tokenizer")
        model = AutoModelForCausalLM.from_pretrained(self.model_id)
        print("Loaded: LLM")
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        print("Loaded: pipeline")
        llm = HuggingFacePipeline(pipeline=pipe)
        print("Loaded: Connector")
        self.llm_chain = LLMChain(prompt=self.prompt, llm=llm)
        print("Loaded: Chain")
        self.next(self.ask_question)

    @step
    def ask_question(self):
        """Ask the question and generate the answer."""
        print(self.llm_chain.run(self.question))
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    load_dotenv()
    PromptFlow()
