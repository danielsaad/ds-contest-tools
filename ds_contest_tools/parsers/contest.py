from .. import contest, metadata
from .common import *


def process_contest(problems_dir: list, output_dir: str, pdf: bool, io: bool) -> None:
    """
    Process the contest files.

    Args:
        problems_dir: list of problems directories.
        output_dir: output directory.
        pdf: Wheter is to generate contest PDFs.
        io: Wheter is to generate contest input/output files.
    """
    setup_and_validate_paths(problems_dir, output_dir)
    os.makedirs(output_dir, exist_ok=True)
    for problem in metadata.Paths().get_problem_dir():
        contest.verify_problem(problem)

    info_log('Generating contest files')
    if io:
        contest.build_input_output()
    elif pdf:
        contest.build_contest_pdf()
    else:
        contest.build_boca_packages()
        contest.build_contest_pdf()
    info_log('Contest files generated successfully')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'contest' commands.

    Args:
        subparsers: The argparse subparsers object.
    """
    contest_parser = subparsers.add_parser(
        'contest', help='build contest files')
    contest_parser.add_argument(
        '-p', '--pdf', action='store_true', default=False, help='generate contest PDFs')
    contest_parser.add_argument('-i', '--io', action='store_true',
                                default=False, help='generate contest input/output files')
    contest_parser.add_argument(
        'problem_dir', help='path to problem(s)', nargs='+')
    contest_parser.add_argument(
        'contest_dir', help='directory which the contest will be saved')
    contest_parser.set_defaults(function=lambda options: process_contest(
        options.problem_dir, options.contest_dir, options.pdf, options.io))
