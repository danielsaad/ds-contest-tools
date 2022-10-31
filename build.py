#!/usr/bin/python3
"""Tool to initialize, build and convert a competitive problem.

Usage:
    ./build.py [mode] [ID]

Author:
    Daniel Saad Nogueira Nunes
"""


# TODO: clean temporary files


import sys
import os
import shutil
import argparse
import logging
from utils import start_log
from jsonutils import parse_json
from pdfutils import build_pdf
from fileutils import recursive_overwrite
from boca import boca_pack
from toolchain import build_executables, run_programs


class statement_metadata:
    def __init__(self, problem_id='', title='', timelimit=0, author=''):
        self.problem_id = problem_id
        self.title = title
        self.timelimit = timelimit
        self.author = author


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', '--all', action='store_true',
                        default=False, help='apply action on all problems')
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='set problem to interative on init')
    parser.add_argument(
        'mode', choices=['init', 'build', 'genio', 'genpdf', 'pack2boca'], help='init: init a problem.\nbuild: build a problem.\ngenio: gen problem input/output while validating inputs.\ngenpdf: generates problem and tutorial PDFs.\npack2boca: pack a problem to BOCA format.\n')
    parser.add_argument('problem_id', nargs='?')
    return parser


def genio(problem_folder) -> None:
    """Call functions to generate the input/output of the problem."""
    build_executables(problem_folder)
    run_programs(problem_folder)


def genpdf(problem_folder) -> None:
    """Call functions to generate the pdf document of the problem."""
    build_pdf(problem_folder)


def build(problem_folder) -> None:
    """Call functions to build a problem."""
    build_executables(problem_folder)
    run_programs(problem_folder)
    genpdf(problem_folder)


def init(problem_folder, interactive=False) -> None:
    """Initialize a competitive problem."""
    if (os.path.exists(problem_folder)):
        print("Problem ID already exists in the directory")
        sys.exit(1)
    folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'arquivos')
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


def pack2boca(problem_folder) -> None:
    """Call funtions to convert the format of the problem to BOCA."""
    boca_pack(problem_folder)


def pack2uri(problem_id):
    print('Not implemented')
    pass


def packall2uri():
    print('Not implemented')
    pass


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if (not args.all and not args.problem_id):
        parser.error(args.mode + ' mode requires a problem id. Usage:' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    start_log()
    if (args.mode == 'init'):
        logging.info('Initializing problem ' + args.problem_id)
        init(args.problem_id, args.interactive)
        print('Problem', args.problem_id, 'initialized')
    elif (args.mode == 'build'):
        logging.info("Building problem " + args.problem_id)
        build(args.problem_id)
    elif (args.mode == 'pack2boca'):
        pack2boca(args.problem_id)
    elif (args.mode == 'genpdf'):
        genpdf(args.problem_id)
    elif (args.mode == 'genio'):
        genio(args.problem_id)
