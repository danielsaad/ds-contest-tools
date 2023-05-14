from ..toolchain import init_problem
from .common import *


def process_init(problem_dir: str, interactive: bool) -> None:
    """Initialize a problem.

    Args:
        problem_dir: The path to the problem directory.
        interactive: Whether the problem is interactive or not.
    """
    setup_and_validate_paths(problem_dir)
    problem_name = get_basename(problem_dir)
    info_log('Initializing problem ' + problem_name)
    init_problem(interactive)
    info_log(f"Problem {problem_name} initialized")


def add_parser(subparsers):
    """Add a subparser for the 'init' command.
    
    Args:
        subparsers: The argparse subparsers object.
    """
    parser_init = subparsers.add_parser('init', help='initialize problem')
    parser_init.add_argument('problem_dir', help='path to the problem directory')
    parser_init.add_argument('-i', '--interactive', action='store_true',
                             default=False, help='set problem to interactive')
    parser_init.set_defaults(function=lambda options: process_init(
        options.problem_dir, options.interactive))
