import yaml
from pathlib import Path

# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"


def load_config():
    """
    Loads the YAML configuration file.

    Returns:
        dict: The configuration dictionary.

    Raises:
        FileNotFoundError: If config.yaml is missing.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    return config


# Load config on module import for easy access
try:
    config = load_config()
except Exception as e:
    print(f"Error loading config: {e}")
    config = {}
