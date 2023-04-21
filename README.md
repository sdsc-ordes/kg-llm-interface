# kg-llm-interface
Langchain-powered natural language interface to RDF knowledge-graphs.

## Installation

This repository uses poetry for package management. A Makefile rule is provided to install the dependencies:

```bash
make install
```

## Usage

The repository contains a [metaflow](https://metaflow.org/) to orchestrate pipelines.
The pipelines are defined in [aikg/pipelines](aikg/pipeline) and can be executed with `python src/pipelines/<pipeline>.py run`.

## Pipelines

* [prompt_llm.py](aikg/pipeline/prompt_llm.py): Prompt a language model with an input question.
