import yaml
from pathlib import Path

# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"


def load_config():
    """
    Loads the YAML configuration file.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    return cfg


# Load config on module import for easy access
try:
    config = load_config()
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}


def get_llm_config():
    """Returns the LLM configuration section."""
    return config.get("models", {}).get("llm", {})


def get_llm_type():
    """Returns the configured LLM engine type (llama or qwen)."""
    return get_llm_config().get("engine_type", "llama")
