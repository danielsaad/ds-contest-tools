import os
from math import floor

from ds_contest_tools.builder import execute_build
from ds_contest_tools.models.build_options import BuildOptions

from .common import *

def cli_handler(problem_dir, all, specific, cpu_count, io, pdf, no_validator, no_generator, no_checker, no_output, ngvoc) -> None:
    """
    Handle the command line interface for the build command.

    Args:
        problem_dir: The directory of the problem to build.
        all: Whether to build all solutions.
        specific: The specific solution to build.
        cpu_count: The number of CPU threads to use.
        io: Whether to generate input/output files.
        pdf: Whether to generate PDFs.
        no_validator: Whether to skip validation.
        no_generator: Whether to skip generation.
        no_checker: Whether to skip checking.
        no_output: Whether to skip output generation.
        ngvoc: Whether to build only executables and PDFs.
    """
    logger.info_log(f"Building problem in {problem_dir}")
    setup_and_validate_paths(problem_dir)
    options: BuildOptions = BuildOptions(all_solutions=all, specific_solution=specific, 
                                         cpu_count=cpu_count, io=io, pdf=pdf, no_validator=no_validator, no_generator=no_generator, no_checker=no_checker, no_output=no_output, ngvoc=ngvoc, problem_dir=problem_dir)

    execute_build(options)

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
        '-no', '--no-output', help='build problem without generating output', action='store_true')
    parser_build.add_argument(
        '-nc', '--no-checker', help='build problem without running the checker', action='store_true')
    parser_build.add_argument(
        '-ngvoc', help='build only problem executables and PDFs', action='store_true')
    parser_build.add_argument('problem_dir', help='path to the problem directory')
    parser_build.set_defaults(function=lambda options: cli_handler(
        problem_dir=options.problem_dir, all=options.all, specific=options.specific, cpu_count=options.cpu_count, io=options.io, pdf=options.pdf, no_validator=options.no_validator, no_generator=options.no_generator, no_checker=options.no_checker, no_output=options.no_output, ngvoc=options.ngvoc))
