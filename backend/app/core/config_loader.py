import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "easm.yaml"


def load_easm_config() -> dict:
    if not CONFIG_PATH.exists():
        raise RuntimeError("EASM config file missing")

    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
