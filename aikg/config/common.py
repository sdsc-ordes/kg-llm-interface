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
