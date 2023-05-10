import os
from math import floor

from .common import *
from .. import toolchain
from .. import pdfutils

def process_build(problem_dir: str, all_solutions: bool, specific_solution: str, cpu_count: int) -> None:
    """Build a problem.

    Args:
        problem_dir: Path to the problem directory.
        all_solutions: Whether to build all solutions or not.
        specific_solution: Name of the solution to be checked.
        cpu_count: Number of threads to be used when checking solutions.
    """
    setup_and_validate_paths(problem_dir)
    problem_name = get_basename(problem_dir)

    info_log(f'Building problem {problem_name}')
    toolchain.build_executables()
    if all_solutions:
        toolchain.run_programs(all_solutions=all_solutions,
                               cpu_number=max(cpu_count, 1))
    elif specific_solution:
        toolchain.run_programs(specific_solution=specific_solution,
                               cpu_number=max(cpu_count, 1))
    else:
        toolchain.run_programs()
    pdfutils.build_pdf()
    info_log(f'Problem {problem_name} built succesfully')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'build' command.

    Args:
        subparsers: The argparse subparsers object.
    """
    parser_build = subparsers.add_parser(
        'build', help='build problem with main solution')

    # Avoid the use of all and specific solution at the same time
    mut_ex_group = parser_build.add_mutually_exclusive_group()
    mut_ex_group.add_argument('-a', '--all', action='store_true',
                              default=False, help='build problem with all solutions')
    mut_ex_group.add_argument(
        '-s', '--specific', help='build problem with specific solution')

    default_threads = max(floor(os.cpu_count() * 0.7), 1)
    parser_build.add_argument('-c', '--cpu-count', help="number of threads to be used "
                              f"when checking solutions. Default is {default_threads} threads.",
                              type=int, default=default_threads)
    parser_build.add_argument(
        'problem_dir', help='path to the problem directory')
    parser_build.set_defaults(function=lambda options: process_build(
        options.problem_dir, options.all, options.specific, options.cpu_count))
