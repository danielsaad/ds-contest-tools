import os

from .common import *
from .. import toolchain


def process_init(problem_dir: str, interactive: bool) -> None:
    """
    Initialize a problem.

    Args:
        problem_dir: The path to the problem directory.
        interactive: Whether the problem is interactive or not.
    """
    validate_paths(problem_dir)
    toolchain.init_problem(interactive)
    info_log(f"Problem {os.path.basename(problem_dir)} initialized")


def add_parser(subparsers):
    """
    Add a subparser for the 'init' command.
    
    Args:
        subparsers: The argparse subparsers object.
    """
    parser_init = subparsers.add_parser('init', help='initialize problem')
    parser_init.add_argument('problem_dir', help='path to the problem directory')
    parser_init.add_argument('-i', '--interactive', action='store_true',
                             default=False, help='set problem to interactive')
    parser_init.set_defaults(function=lambda options: process_init(
        options.problem_dir, options.interactive))
