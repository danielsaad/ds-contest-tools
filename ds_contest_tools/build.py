import argparse
import os
import shutil
import sys
from math import floor

from .logger import error_log, info_log
from .metadata import Paths
from .pdfutils import build_pdf
from .toolchain import build_executables, clean_files, run_programs
from .utils import instance_paths, verify_path


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='init interactive problem')
    parser.add_argument('-a', '--all', action='store_true',
                        default=False, help='build problem with all solutions')
    parser.add_argument('-s', '--specific',
                        help='build problem with specific solution')
    default_threads = max(floor(os.cpu_count() * 0.7), 1)
    parser.add_argument('-c', '--cpu-count', help=f"number of threads to be used when checking solutions. Default is {default_threads} threads.",
                        type=int, default=default_threads)
    parser.add_argument(
        'mode', choices=['init', 'build', 'genio', 'genpdf', 'clean'],
        help='init: init a problem.\nbuild: build a problem.\n' +
        'genio: gen problem input/output while validating inputs.\n' +
        'genpdf: generates problem and tutorial PDFs.\n' +
        'clean: remove executables of a DS problem.\n')
    parser.add_argument('problem_id', nargs='?')
    return parser


def genio(all_solutions=False) -> None:
    """Call functions to generate the input/output of the problem."""
    build_executables()
    run_programs(all_solutions)


def genpdf() -> None:
    """Call functions to generate the pdf document of the problem."""
    build_pdf()


def build(all_solutions=False, specific_solution: str = '', cpu_number: int = 1) -> None:
    """Call functions to build a problem."""
    build_executables()
    if all_solutions:
        run_programs(all_solutions=all_solutions,
                     cpu_number=max(cpu_number, 1))
    elif specific_solution:
        run_programs(specific_solution=specific_solution,
                     cpu_number=max(cpu_number, 1))
    else:
        run_programs()
    genpdf()



def clean() -> None:
    """Call functions to clean executables"""
    clean_files()


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if not args.problem_id:
        parser.error(args.mode + ' mode requires a problem id. Usage: ' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    instance_paths(args.problem_id)
    if args.mode != 'init':
        verify_path(args.problem_id)

    if (args.mode == 'init'):
        info_log('Initializing problem ' + args.problem_id)
        info_log('Problem ' + args.problem_id + ' initialized.')
    elif (args.mode == 'build'):
        info_log("Building problem " + args.problem_id)
        build(args.all, args.specific, args.cpu_count)
        info_log("Problem " + args.problem_id + " built")
    elif (args.mode == 'genpdf'):
        genpdf()
        info_log("PDFs generated.")
    elif (args.mode == 'genio'):
        info_log("Generating input and output")
        genio(args.all)
        info_log("Input and output generated.")
    elif (args.mode == 'clean'):
        clean()
        info_log('Executables removed')
