"""Tool to convert problems into DS, BOCA, Polygon or SQTPM format.

Usage:
    python3 convert.py [flags] [initial_format] [final_format] [problem_folder]

Author:
    Daniel Saad Nogueira Nunes
"""


import os
import sys
import argparse
from json import dumps
from getpass import getpass
from sqtpm import convert_to_sqtpm
from polygon_submitter import send_to_polygon
from polygon_converter import get_polygon_problem


def create_parser():
    """Initialize tool parsers."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='list of commands',
        description='',
        help='DESCRIPTION',
        metavar='COMMAND',
        required=True
    )

    ds_parser = subparsers.add_parser(
        'convert', help='Convert DS problem to another format')
    ds_parser.add_argument('format', choices=['BOCA', 'Polygon', 'SQTPM'],
                           help='BOCA: convert problem to BOCA.\n' +
                           'Polygon: convert problem to Polygon.' +
                           'SQTPM: convert problem to SQTPM.')
    ds_parser.add_argument(
        'problem_dir', help='Problem directory')
    ds_parser.add_argument(
        'output_dir', help='Folder of converted folder or ID of Polygon problem.')
    ds_parser.set_defaults(function=lambda options: start_conversion(options))

    polygon_parser = subparsers.add_parser(
        'convert_polygon', help='Convert problem from Polygon')
    polygon_parser.add_argument(
        'problem_id', help='Polygon problem ID or directory if local.')
    polygon_parser.add_argument('-l', '--local', action='store_true')
    polygon_parser.set_defaults(
        function=lambda options: start_polygon_conversion(options))

    keys_parser = subparsers.add_parser(
        'change_keys', help='Change Polygon API keys')
    keys_parser.set_defaults(
        function=lambda options: change_polygon_keys(options))

    options = parser.parse_args()
    options.function(options)


def start_polygon_conversion(options):
    """Convert problem from Polygon to DS."""
    if not options.local:
        verify_polygon_keys()
    get_polygon_problem(options.problem_dir, options.local)
    print('Problem converted successfully.')


def start_conversion(options):
    """Convert problem from DS to Polygon, SQTPM or BOCA."""
    if options.format == 'Polygon':
        verify_polygon_keys()
        send_to_polygon(options.problem_dir)
    elif options.format == 'SQTPM':
        convert_to_sqtpm(options.problem_dir, options.output_dir)
    else:
        print('Not implemented yet.')
        sys.exit(0)
    print('Problem converted successfully.')


def change_polygon_keys(options) -> None:
    """Create or change keys for Polygon API."""
    apiKey = getpass("apiKey: ")
    secret = getpass("secret: ")
    keys = {
        'apiKey': apiKey,
        'secret': secret
    }
    with open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'secrets.json'), 'w') as f:
        f.write(dumps(keys))

    print('Keys saved. They are stored locally in the tool directory.')


def verify_polygon_keys() -> None:
    """Check if Polygon API keys file is created."""
    tool_path = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(tool_path, 'secrets.json')

    if not os.path.exists(secrets_path):
        print("Keys are not defined. Use 'change_keys' to define it.")
        sys.exit(1)


if __name__ == '__main__':
    create_parser()
