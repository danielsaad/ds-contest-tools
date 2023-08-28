from ..contest import *
from ..metadata import Paths
from .common import *


def process_contest(problems_dir: list, output_dir: str, pdf: bool, io: bool, author: bool, no_verify: bool) -> None:
    """
    Process the contest files.

    Args:
        problems_dir: list of problems directories.
        output_dir: output directory.
        pdf: Whether is to generate only contest PDFs.
        io: Whether is to generate only contest input/output files.
        author: Whether is to add author name to PDFs.
        no_verify: Whether is to verify and rebuild problems.
    """
    setup_and_validate_paths(problems_dir, output_dir, additional_verification=['pdfjam'])
    os.makedirs(output_dir, exist_ok=True)
    
    if not no_verify:
        for problem in Paths().get_problem_dir():
            verify_problem(problem)

    info_log('Generating contest files')
    if io:
        build_input_output()
    elif pdf:
        build_contest_pdf(author=author)
    else:
        build_boca_packages(author=author)
        build_contest_pdf(author=author)
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
    contest_parser.add_argument('--author', action='store_true', help='add author name to PDFs')
    contest_parser.add_argument('-nv', '--no-verify', action='store_true', help='do not verify and rebuild problems', default=False)
    contest_parser.add_argument(
        'problem_dir', help='path to problem(s)', nargs='+')
    contest_parser.add_argument(
        'contest_dir', help='directory which the contest will be saved')
    contest_parser.set_defaults(function=lambda options: process_contest(
        options.problem_dir, options.contest_dir, options.pdf, options.io, options.author, options.no_verify))
