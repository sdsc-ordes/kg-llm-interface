from pathlib import Path
import yaml

config_files = Path(__file__).parent.glob("*.yaml")
config = {cfg.stem: yaml.safe_load(open(cfg)) for cfg in config_files}
