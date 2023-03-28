import json
import os
import sys


def parse_json(json_file: str) -> dict:
    """Converts a JSON file to a Python dictionary.

    Args:
        json_file: The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    json_data = {}

    if not os.path.isfile(json_file):
        print(os.path.basename(json_file), 'does not exists.')
        sys.exit(1)

    with open(json_file) as f:
        json_data = json.load(f)

    return json_data
