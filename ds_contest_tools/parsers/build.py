import os
from math import floor

from ..pdfutils import build_pdf
from ..toolchain import build_executables, run_programs
from .common import *


def process_build(problem_dir: str, all_solutions: bool, specific_solution: str, cpu_count: int, io: bool, pdf: bool, no_validator: bool, no_generator: bool) -> None:
    """Build a problem.

    Args:
        problem_dir: Path to the problem directory.
        all_solutions: Whether to build all solutions or not.
        specific_solution: Name of the solution to be checked.
        cpu_count: Number of threads to be used when checking solutions.
        io: Whether to generate only input/output files or not.
        pdf: Whether to generate only PDFs or not.
        no_validator: Whether to build problem without the validator or not.
        no_generator: Whether to build problem without the generator or not.
    """
    setup_and_validate_paths(problem_dir)
    problem_name = get_basename(problem_dir)

    if pdf:
        info_log('Generating problem PDF')
        build_pdf()
        info_log('Problem PDF generated successfully')
    elif io:
        info_log("Generating input/output")
        build_executables()
        run_programs(all_solutions=all_solutions, specific_solution=specific_solution,
                     cpu_number=cpu_count, no_validator=no_validator, no_generator=no_generator)
        info_log("Input/output generated successfully")
    else:
        info_log(f'Building problem {problem_name}')
        build_executables()
        run_programs(all_solutions=all_solutions, specific_solution=specific_solution,
                     cpu_number=cpu_count, no_validator=no_validator, no_generator=no_generator)
        build_pdf()
        info_log(f'Problem {problem_name} built successfully')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'build' command.

    Args:
        subparsers: The argparse subparsers object.
    """
    parser_build = subparsers.add_parser(
        'build', help='build problem with main solution')

    # Avoid the use of wrong combinations of arguments
    mut_ex_group = parser_build.add_mutually_exclusive_group()
    mut_ex_group.add_argument('-a', '--all', action='store_true',
                              default=False, help='build problem with all solutions')
    mut_ex_group.add_argument(
        '-s', '--specific', type=str, default='', help='build problem with specific solution')
    mut_ex_group.add_argument(
        '-p', '--pdf', action='store_true', default=False, help='generate only problem PDFs')
    mut_ex_group.add_argument('-i', '--io', action='store_true',
                              default=False, help='generate only problem input/output files')

    default_threads = max(floor(os.cpu_count() * 0.7), 1)
    parser_build.add_argument('-c', '--cpu-count', help="number of threads to be used "
                              f"when checking solutions. Default is {default_threads} threads.",
                              type=int, default=default_threads)
    parser_build.add_argument(
        '-nv', '--no-validator', help='build problem without the validator', action='store_true')
    parser_build.add_argument(
        '-ng', '--no-generator', help='build problem without the generator', action='store_true')
    parser_build.add_argument(
        'problem_dir', help='path to the problem directory')
    parser_build.set_defaults(function=lambda options: process_build(
        options.problem_dir, options.all, options.specific, options.cpu_count, options.io, options.pdf, options.no_validator, options.no_generator))
