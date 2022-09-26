#!/usr/bin/python3

# TODO: clean temporary files


import sys
import os
import shutil
import argparse
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


def genio(problem_folder):
    build_executables(problem_folder)
    run_programs(problem_folder)


def genpdf(problem_folder):
    build_pdf(problem_folder)


def build(problem_folder):
    build_executables(problem_folder)
    run_programs(problem_folder)
    genpdf(problem_folder)


def build_all():
    problem_ids = [f for f in os.listdir(
        'Problemas') if os.path.isdir(os.path.join('Problemas', f))]
    for id in problem_ids:
        build(id)


def init(problem_folder, interactive=False):
    folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'arquivos')
    shutil.copytree(folder, problem_folder,
                    ignore=shutil.ignore_patterns('boca'))
    # Rename files and folders if the problem is interactive
    interactive_statement = os.path.join(
        problem_folder, 'statement-interactive.md')
    interactor = os.path.join(*[problem_folder, 'src', 'interactor.cpp'])
    interactive_json = os.path.join(problem_folder, 'problem-interactive.json')
    if(interactive):
        shutil.move(interactive_statement, os.path.join(
            problem_folder, 'statement.md'))
        shutil.move(interactive_json, os.path.join(
            problem_folder, 'problem.json'))
    else:
        os.remove(interactive_statement)
        os.remove(interactive_json)
        os.remove(interactor)


def pack2boca(problem_folder):
    boca_pack(problem_folder)


def packall2boca():
    problem_ids = [f for f in os.listdir(
        'Problemas') if os.path.isdir(os.path.join('Problemas', f))]
    for id in problem_ids:
        pack2boca(id)


def pack2uri(problem_id):
    print('Not implemented')
    pass


def packall2uri():
    print('Not implemented')
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        default=False, help='apply action on all problems')
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='set problem do interative on init')
    parser.add_argument(
        'mode', choices=['init', 'build', 'buildall', 'genio', 'genpdf', 'pack2boca', 'packall2boca'], help='\ninit: init a problem\nbuild: build  a problem.\ngenio: generates problem input/output while validating inputs\ngenpdf: generates problem and tutorial PDFs.\npack2boca: pack a problem to BOCA format.\n')
    parser.add_argument('problem_id', nargs='?')
    args = parser.parse_args()
    if(not args.all and not args.problem_id):
        parser.error(args.mode + ' mode requires a problem id. Usage:' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    new_path = os.path.dirname(sys.argv[0])
    if (new_path != ''):
        os.chdir(new_path)
    if(args.mode == 'init'):
        print('Initializing problem', args.problem_id)
        init(args.problem_id, args.interactive)
        print('Problem', args.problem_id, 'initialized')
    elif(args.mode == 'build'):
        if(not args.all):
            print("Building problem", args.problem_id)
            build(args.problem_id)
        else:
            build_all()
    elif(args.mode == 'pack2boca'):
        if(not args.all):
            pack2boca(args.problem_id)
        else:
            packall2boca()
    elif(args.mode == 'genpdf'):
        genpdf(args.problem_id)
    elif(args.mode == 'genio'):
        genio(args.problem_id)
