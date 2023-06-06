from ..contest import *
from ..metadata import Paths
from .common import *


def process_contest(problems_dir: list, output_dir: str, pdf: bool, io: bool) -> None:
    """
    Process the contest files.

    Args:
        problems_dir: list of problems directories.
        output_dir: output directory.
        pdf: Whether is to generate only contest PDFs.
        io: Whether is to generate only contest input/output files.
    """
    setup_and_validate_paths(problems_dir, output_dir, additional_verification=['pdfjam'])
    os.makedirs(output_dir, exist_ok=True)
    for problem in Paths().get_problem_dir():
        verify_problem(problem)

    info_log('Generating contest files')
    if io:
        build_input_output()
    elif pdf:
        build_contest_pdf()
    else:
        build_boca_packages()
        build_contest_pdf()
    info_log('Contest files generated successfully')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'contest' commands.

    Args:
        subparsers: The argparse subparsers object.
    """
    contest_parser = subparsers.add_parser(
        'contest', help='build contest files')
    mut_ex_group = contest_parser.add_mutually_exclusive_group()
    mut_ex_group.add_argument(
        '-p', '--pdf', action='store_true', default=False, help='generate contest PDFs')
    mut_ex_group.add_argument('-i', '--io', action='store_true',
                                default=False, help='generate contest input/output files')
    contest_parser.add_argument(
        'problem_dir', help='path to problem(s)', nargs='+')
    contest_parser.add_argument(
        'contest_dir', help='directory which the contest will be saved')
    contest_parser.set_defaults(function=lambda options: process_contest(
        options.problem_dir, options.contest_dir, options.pdf, options.io))
