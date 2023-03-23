"""Tool to convert problems into DS, BOCA, Polygon or SQTPM format.

Usage:
    python3 convert.py <command> [<flags>]

Author:
    Daniel Saad Nogueira Nunes
"""


import argparse
import os
import sys
from getpass import getpass
from json import dumps

from polygon_converter import get_polygon_problem
from polygon_submitter import send_to_polygon
from sqtpm import convert_to_sqtpm


def create_parser():
    """Initialize tool parsers."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(
        title='list of commands',
        description='',
        help='DESCRIPTION',
        metavar='COMMAND',
        required=True
    )

    ds_parser = subparsers.add_parser(
        'convert', help='Convert DS problem to another format.')
    ds_parser.add_argument('format', choices=['BOCA', 'Polygon', 'SQTPM'],
                           help='Format to convert the problem.')
    ds_parser.add_argument(
        'problem_dir', help='Path to the problem directory.')
    ds_parser.add_argument(
        'output_dir', help='Output directory of the converted problem or ID of the Polygon problem.')
    ds_parser.set_defaults(function=lambda options: start_conversion(
        options.problem_dir, options.output_dir, options.format))

    polygon_parser = subparsers.add_parser(
        'convert_polygon', help='Convert problem from Polygon.')
    polygon_parser.add_argument(
        'problem_id', help='Polygon problem ID or directory if local.')
    polygon_parser.add_argument('-l', '--local', action='store_true')
    polygon_parser.set_defaults(
        function=lambda options: start_polygon_conversion(options.problem_dir, options.local))

    keys_parser = subparsers.add_parser(
        'change_keys', help='Change Polygon API keys.')
    keys_parser.set_defaults(
        function=lambda _: change_polygon_keys())

    options = parser.parse_args()
    options.function(options)


def start_polygon_conversion(problem_dir: str, local: str) -> None:
    """Convert problem from Polygon to DS."""
    if not local:
        verify_polygon_keys()
    get_polygon_problem(problem_dir, local)
    print('Problem converted successfully.')


def start_conversion(problem_dir: str, output_dir: str, problem_format: str) -> None:
    """Convert problem from DS to Polygon, SQTPM or BOCA."""
    if problem_format == 'Polygon':
        verify_polygon_keys()
        send_to_polygon(problem_dir)
    elif problem_format == 'SQTPM':
        convert_to_sqtpm(problem_dir, output_dir)
    else:
        print('Not implemented yet.')
        sys.exit(0)
    print('Problem converted successfully.')


def change_polygon_keys() -> None:
    """Create or change keys for Polygon API."""
    api_key = getpass("apiKey: ")
    if not api_key:
        print("API Key cannot be empty.")
        sys.exit(1)
    secret = getpass("secret: ")
    if not secret:
        print("API Secret cannot be empty.")
        sys.exit(1)
    keys = {
        'apiKey': api_key,
        'secret': secret
    }
    with open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'secrets.json'), 'w') as f:
        f.write(dumps(keys))

    print('Keys saved. They are locally stored in the tool directory.')


def verify_polygon_keys() -> None:
    """Check if Polygon API keys file is created."""
    tool_path = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(tool_path, 'secrets.json')

    if not os.path.exists(secrets_path):
        print("Keys are not defined. Use 'change_keys' to define it.")
        sys.exit(1)


if __name__ == '__main__':
    create_parser()
