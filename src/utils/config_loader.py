import json
import os
from pathlib import Path
from typing import Any


def load_config(config_path: str = r'config\main_config.json') -> dict[str, Any]:
    """
    Loads configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration JSON file.

    Returns:
        Dict[str, Any]: Parsed configuration as a dictionary.
    """
    with Path(config_path).open() as f:
        return json.load(f)
    

if __name__ == "__main__":
    path=r'config\main_config.json'
    config = load_config(path)
    print(config)
