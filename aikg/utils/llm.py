# kg-llm-interface
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from langchain import LLMChain, PromptTemplate
from langchain.llms.base import LLM


def setup_llm_chain(llm: LLM, prompt_template: str) -> LLMChain:
    """Prepare the prompt injection and text generation system."""
    # Auto-detecting prompt variables surrounded by single curly braces
    variables = re.findall(r"[^{]{([^} \n]+)}[^}]", prompt_template)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=variables,
    )
    return LLMChain(prompt=prompt, llm=llm)
