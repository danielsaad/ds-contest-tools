import json
import os
import sys


def parse_json(json_file: str) -> dict:
    """Receives a path to a '.json' file and converts it to a dict."""
    json_data = {}

    if not os.path.isfile(json_file):
        print(os.path.basename(json_file), 'does not exists.')
        sys.exit(1)

    with open(json_file) as f:
        json_data = json.load(f)
    return json_data
