import argparse
import os
import sys
from getpass import getpass
from typing import Union

from boca import generate_boca_pack
from fileutils import check_interactive_problem
from jsonutils import write_to_json
from logger import error_log, info_log
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

    ds_parser = subparsers.add_parser('convert_to', help='Convert DS problem to another format.')
    ds_parser.add_argument('format', choices=['boca', 'polygon', 'sqtpm'], help='Format to convert the problem.')
    ds_parser.add_argument('problem_dir', help='Path to the problem directory.')
    ds_parser.add_argument('-o', '--output_dir', 
                           help='Path to save the converted problem or ID of the Polygon problem, if one is not defined yet. Default output directory is the problem directory.')
    ds_parser.set_defaults(function=lambda options: start_conversion_to(options.format, options.problem_dir, options.output_dir))

    polygon_parser = subparsers.add_parser('convert_from', help='Convert problem from some format to DS format.')
    polygon_parser.add_argument('format', choices=['polygon'], help='Format to convert the problem.')
    polygon_parser.add_argument('problem_dir', help='Path to store the converted problem.')
    polygon_parser.add_argument('package_dir', help='Path to the problem package or Polygon ID')
    polygon_parser.add_argument('-l', '--local', action='store_true', help='Convert local Polygon package. Use the package path instead of ID in package_dir.')
    polygon_parser.set_defaults(function=lambda options: start_conversion_from(options.format, options.problem_dir, options.package_dir, options.local,))

    keys_parser = subparsers.add_parser('set_keys', help='Change Polygon API keys.')
    keys_parser.set_defaults(function=lambda _: change_polygon_keys())

    options = parser.parse_args()
    options.function(options)


def start_conversion_from(problem_format: str, problem_dir: str, package_dir: str, local: bool) -> None:
    """Convert problem from Polygon to DS."""
    if problem_format == 'polygon':
        if not local:
            verify_polygon_keys()
        get_polygon_problem(problem_dir, package_dir, local)
        info_log('Problem converted successfully.')
    else:
        info_log('Not implemented yet.')


def start_conversion_to(problem_format: str, problem_dir: str, output_dir: Union[str, None]) -> None:
    """Convert problem from DS to Polygon, SQTPM or BOCA."""
    interactive = check_interactive_problem(problem_dir)
    if problem_format != 'polygon' and interactive:
        error_log(f'Interactive problems are not supported by {problem_format} format.')
        sys.exit(0)

    if problem_format == 'polygon':
        verify_polygon_keys()
        send_to_polygon(problem_dir, output_dir)
    elif problem_format == 'sqtpm':
        convert_to_sqtpm(problem_dir, output_dir)
    elif problem_format == 'boca':
        generate_boca_pack(problem_dir, output_dir)
    else:
        error_log('Not implemented yet.')
        sys.exit(0)
    info_log('Problem converted successfully.')


def change_polygon_keys() -> None:
    """Prompts the user to enter their Polygon API keys and saves them to a local file."""
    api_key = getpass("API key: ")
    if not api_key:
        error_log("API key cannot be empty.")
        sys.exit(1)
    secret = getpass("API secret: ")
    if not secret:
        error_log("API secret cannot be empty.")
        sys.exit(1)
    keys = {
        'apikey': api_key,
        'secret': secret
    }
    write_to_json(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'secrets.json'), keys)
    info_log('Keys saved. They are stored locally in the tool directory.')


def verify_polygon_keys() -> None:
    """Check if the Polygon API keys file has been created and is accessible.

    The function checks whether the `secrets.json` file that contains the 
    Polygon API keys exists in the directory of this script.
    """
    tool_path = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(tool_path, 'secrets.json')

    if not os.path.exists(secrets_path):
        error_log("Keys are not defined. Use 'set_keys' to define it.")
        sys.exit(1)


if __name__ == '__main__':
    create_parser()
