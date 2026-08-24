import os
from math import floor

from ds_contest_tools.builder import execute_build
from ds_contest_tools.parsers.dto.build_options import BuildOptions

from .common import *

def cli_handler(args) -> None:
    """
    Handle the command line interface for the build command.

    Args:
        args: The parsed command line arguments.
    """
    setup_and_validate_paths(args.problem_dir)
    options: BuildOptions = BuildOptions(args.all, args.specific, args.cpu_count, args.io, args.pdf, args.no_validator, args.no_generator, args.no_checker, args.no_output, args.ngvoc)

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
        options.problem_dir, options.all, options.specific, options.cpu_count, options.io, options.pdf, options.no_validator, options.no_generator, options.no_checker, options.no_output, options.ngvoc))
