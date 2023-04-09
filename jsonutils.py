import json
import os
import sys

from logger import error_log


def parse_json(json_file: str) -> dict:
    """Converts a JSON file to a Python dictionary.

    Args:
        json_file: The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    json_data = {}

    if not os.path.isfile(json_file):
        error_log(os.path.basename(json_file), 'does not exists.')
        sys.exit(1)

    with open(json_file) as f:
        json_data = json.load(f)

    return json_data


def write_to_json(path: str, content: dict) -> None:
    """Write dictionary content to a JSON file.

    Args:
        path: Path of the JSON file to be written.
        content: Dictionary containing the keys and values to be written.
    """
    with open(path, 'w') as f:
        f.write(json.dumps(content, ensure_ascii=False))
