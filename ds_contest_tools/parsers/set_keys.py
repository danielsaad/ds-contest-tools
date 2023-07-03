import sys
from getpass import getpass

from ..jsonutils import write_to_json
from .common import *


def process_set_keys() -> None:
    """Prompts the user to enter their Polygon API keys and saves them to a local file."""
    api_key = getpass("API key: ")
    if not api_key:
        error_log("API key can't be empty.")
    secret = getpass("API secret: ")
    if not secret:
        error_log("API secret can't be empty.")
    keys = {
        'apikey': api_key,
        'secret': secret
    }
    write_to_json(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'secrets.json'), keys)
    info_log('Keys saved. They are stored locally in the tool directory.')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'polygon_keys' command.

    Args:
        subparsers: The argparse subparsers object.
    """
    keys_parser = subparsers.add_parser(
        'set_keys', help='set polygon api keys')
    keys_parser.set_defaults(function=lambda _: process_set_keys())
