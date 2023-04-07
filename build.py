import argparse
import os
import shutil
import sys

from boca import boca_pack
from logger import error_log, info_log
from metadata import Paths
from pdfutils import build_pdf
from toolchain import build_executables, clean_files, run_programs
from utils import instance_paths, verify_path


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='init interactive problem')
    parser.add_argument('-a', '--all', action='store_true',
                        default=False, help='buil problem with all solutions')
    parser.add_argument('-s', '--specific',
                        help='build problem with specific solution')
    parser.add_argument(
        'mode', choices=['init', 'build', 'genio', 'genpdf', 'pack2boca', 'clean'],
        help='init: init a problem.\nbuild: build a problem.\n' +
        'genio: gen problem input/output while validating inputs.\n' +
        'genpdf: generates problem and tutorial PDFs.\n' +
        'pack2boca: pack a problem to BOCA format.\n' +
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


def build(all_solutions=False, specific_solution: str = '') -> None:
    """Call functions to build a problem."""
    build_executables()
    if all_solutions:
        run_programs(all_solutions=all_solutions)
    elif specific_solution:
        run_programs(specific_solution=specific_solution)
    else:
        run_programs()
    genpdf()


def init(interactive=False) -> None:
    """Initialize a competitive problem."""
    problem_folder = Paths().get_problem_dir()
    if os.path.exists(os.path.join(problem_folder, 'src')):
        error_log("Problem ID already exists in the directory")
        sys.exit(1)

    folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'files')
    shutil.copytree(folder, problem_folder,
                    ignore=shutil.ignore_patterns('boca'), dirs_exist_ok=True)
    # Rename files and folders if the problem is interactive
    interactor = os.path.join(*[problem_folder, 'src', 'interactor.cpp'])
    interactive_json = os.path.join(problem_folder, 'problem-interactive.json')
    interactor_tex = os.path.join(
        *[problem_folder, 'statement', 'interactor.tex'])
    os.remove(os.path.join(problem_folder, 'sqtpm.sh'))
    if (interactive):
        shutil.move(interactive_json, os.path.join(
            problem_folder, 'problem.json'))
        # Create .interactive files for statement
        os.makedirs(os.path.join(problem_folder, 'input'))
        os.makedirs(os.path.join(problem_folder, 'output'))
        open(os.path.join(
            *[problem_folder, 'input', '1.interactive']), 'w').close()
        open(os.path.join(
            *[problem_folder, 'output', '1.interactive']), 'w').close()
    else:
        os.remove(interactor_tex)
        os.remove(interactive_json)
        os.remove(interactor)


def pack2boca() -> None:
    """Call funtions to convert the format of the problem to BOCA."""
    boca_pack()


def clean() -> None:
    """Call functions to clean executables"""
    clean_files()


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if not args.problem_id:
        parser.error(args.mode + ' mode requires a problem id. Usage: ' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    if args.mode != 'init':
        verify_path(args.problem_id)

    instance_paths(args.problem_id)
    if (args.mode == 'init'):
        info_log('Initializing problem ' + args.problem_id)
        init(args.interactive)
        info_log('Problem ' + args.problem_id + ' initialized.')
    elif (args.mode == 'build'):
        info_log("Building problem " + args.problem_id)
        build(args.all, args.specific)
        info_log("Problem " + args.problem_id + " built")
    elif (args.mode == 'pack2boca'):
        pack2boca()
        info_log("Problem " + args.problem_id + " to BOCA successfully.")
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
