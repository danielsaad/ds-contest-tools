from ..pdfutils import build_pdf
from ..toolchain import build_executables, run_programs
from .common import *


def process_genio(problem_dir: str) -> None:
    """
    Generate problem input/output files.

    Args:
        problem_dir: Path to problem directory.
    """
    setup_and_validate_paths(problem_dir)
    info_log("Generating input/output")
    build_executables()
    run_programs()
    info_log("Input/output generated successfully")


def process_genpdf(problem_dir: str) -> None:
    """
    Generate problem PDFs.

    Args:
        problem_dir: Path to problem directory.
    """
    setup_and_validate_paths(problem_dir)
    info_log('Generating problem PDF')
    build_pdf()
    info_log('Problem PDF generated successfully')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'genpdf' and 'genio' commands.

    Args:
        subparsers: The argparse subparsers object.
    """
    gen_pdf_parser = subparsers.add_parser(
        'genpdf', help='generate problem pdf')
    gen_pdf_parser.add_argument(
        'problem_dir', help='path to problem directory')
    gen_pdf_parser.set_defaults(
        function=lambda options: process_genpdf(options.problem_dir))

    gen_io_parser = subparsers.add_parser(
        'genio', help='generate problem  input/output')
    gen_io_parser.add_argument('problem_dir', help='path to problem directory')
    gen_io_parser.set_defaults(
        function=lambda options: process_genio(options.problem_dir))
