from .common import *
from .. import toolchain


def process_clean(problem_dir: list) -> None:
    """Clean executables of the given problem(s).

    Args:
        problem_paths: List of paths to problem directories.
    """
    validate_paths(problem_dir)
    toolchain.clean_files()
    info_log(f'Executables cleaned succesfully.')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'clean' command.

    Args:
        subparsers: The argparse subparsers object.
    """
    parser_clean = subparsers.add_parser(
        'clean', help='remove problem(s) executables')
    parser_clean.add_argument('problem_dir', help='path to problem directory')
    parser_clean.set_defaults(
        function=lambda options: process_clean(options.problem_dir))
