import os.path

from .common import *
from .. import toolchain, utils


def process_init(problem_dir: str, interactive: bool) -> None:
    utils.instance_paths(problem_dir)
    utils.verify_path(problem_dir)
    toolchain.init_problem(interactive)
    info_log(f"Problem {os.path.basename(problem_dir)} initialized")


def add_parser(subparsers):
    parser_init = subparsers.add_parser('init', help='initialize problem')
    parser_init.add_argument('problem_dir', help='path to the problem directory')
    parser_init.add_argument('-i', '--interactive', action='store_true',
                             default=False, help='set problem to interactive')
    parser_init.set_defaults(function=lambda options: process_init(
        options.problem_dir, options.interactive))
