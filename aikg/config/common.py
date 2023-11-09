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

from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel
import yaml

Config = TypeVar("Config", bound=BaseModel)


def parse_yaml_config(config_path: Path, config_class: Type[Config]) -> Config:
    """Parse a YAML config file into a pydantic model.

    Args:
        config_path: Path to YAML config file.
        config_class: The pydantic model to parse the config into.

    Returns:
        The parsed config.
    """
    # Load dict from YAML file
    config_dict = yaml.safe_load(config_path.read_text())
    return config_class.parse_obj(config_dict)
