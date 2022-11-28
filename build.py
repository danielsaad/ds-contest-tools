#!/usr/bin/python3
"""Tool to initialize, build and convert a competitive problem.

Usage:
    ./build.py [mode] [ID]

Author:
    Daniel Saad Nogueira Nunes
"""


import sys
import os
import shutil
import argparse
from logger import info_log
from pdfutils import build_pdf
from boca import boca_pack
from toolchain import build_executables, run_programs, clean_files
from metadata import Paths


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='set problem to interative on init')
    parser.add_argument(
        'mode', choices=['init', 'build', 'genio', 'genpdf', 'pack2boca', 'clean'], 
                help='init: init a problem.\nbuild: build a problem.\n' +
                'genio: gen problem input/output while validating inputs.\n' +
                'genpdf: generates problem and tutorial PDFs.\n' +
                'pack2boca: pack a problem to BOCA format.\n' + 
                'clean: remove executables of a DS problem.\n')
    parser.add_argument('problem_id', nargs='?')
    return parser


def genio() -> None:
    """Call functions to generate the input/output of the problem."""
    build_executables()
    run_programs()


def genpdf() -> None:
    """Call functions to generate the pdf document of the problem."""
    build_pdf()


def build() -> None:
    """Call functions to build a problem."""
    build_executables()
    run_programs()
    genpdf()


def init(interactive=False) -> None:
    """Initialize a competitive problem."""
    problem_folder = Paths.instance().dirs["problem_dir"]
    if (os.path.exists(problem_folder)):
        print("Problem ID already exists in the directory")
        sys.exit(1)

    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arquivos')
    shutil.copytree(folder, problem_folder,
                    ignore=shutil.ignore_patterns('boca'))
    # Rename files and folders if the problem is interactive
    interactive_statement = os.path.join(
        problem_folder, 'statement-interactive.md')
    interactor = os.path.join(*[problem_folder, 'src', 'interactor.cpp'])
    interactive_json = os.path.join(problem_folder, 'problem-interactive.json')
    if (interactive):
        shutil.move(interactive_statement, os.path.join(
            problem_folder, 'statement.md'))
        shutil.move(interactive_json, os.path.join(
            problem_folder, 'problem.json'))
    else:
        os.remove(interactive_statement)
        os.remove(interactive_json)
        os.remove(interactor)


def pack2boca() -> None:
    """Call funtions to convert the format of the problem to BOCA."""
    boca_pack()


def clean() -> None:
    """Call functions to clean executables"""
    if (not os.path.exists(Paths.instance().dirs["problem_dir"])):
        print("Path to problem does not exists.")
        sys.exit(1)
    clean_files()


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if(not args.problem_id):
        parser.error(args.mode + ' mode requires a problem id. Usage: ' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    Paths.instance(args.problem_id)
    if (args.mode == 'init'):
        info_log('Initializing problem ' + args.problem_id)
        init(args.interactive)
        print('Problem', args.problem_id, 'initialized.')
    elif (args.mode == 'build'):
        info_log("Building problem " + args.problem_id)
        build()
        print("Problem " + args.problem_id + " built.")
    elif (args.mode == 'pack2boca'):
        pack2boca()
        print("Problem " + args.problem_id + " to BOCA successfully.")
    elif (args.mode == 'genpdf'):
        genpdf()
        print("PDFs generated.")
    elif (args.mode == 'genio'):
        genio()
        print("Input and Output generated.")
    elif (args.mode == 'clean'):
        clean()
        print('Files removed successfully.')
