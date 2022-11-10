"""Tool to create a contest by merging competitive problems.

Usage:
    ./contest.py [flags] [mode] [problem_list] [output_folder]

Author:
    Daniel Saad Nogueira Nunes
"""

import subprocess
import sys
import os
import argparse
import shutil
from logger import info_log
from latexutils import clean_auxiliary_files
from pdfutils import build_pdf, merge_pdfs
from boca import boca_pack
from utils import convert_idx_to_string, verify_command


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--boca', action='store_true',
                        default=False, help='build problems in BOCA format.')
    parser.add_argument('mode', choices=['build', 'genpdf'],
                        help='build: create a contest.\n' +
                        'genpdf: generates problem and tutorial PDFs.\n')
    parser.add_argument('problem_path', help='path to the problem.',
                        nargs='+')
    parser.add_argument(
        'contest_folder', help='directory which the contest will be saved.')
    return parser


def build_contest_pdf(problem_folder_l: str, output_folder: str) -> None:
    """Builds a contest pdf from the PDFs of the list of problems"""
    info_log('Creating contest PDF')
    problem_pdf_l = []
    tutorial_pdf_l = []

    cls_file = os.path.join(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'arquivos'), 'maratona.cls')
    shutil.copy(cls_file, output_folder)

    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': False,
                   'problem_label': label}
        build_pdf(folder, output_folder, options)
        basename = os.path.basename(folder)
        problem_pdf_l.append(os.path.join(output_folder, basename+'.pdf'))
        tutorial_pdf_l.append(os.path.join(
            output_folder, basename+'-tutorial.pdf'))
    clean_auxiliary_files(output_folder)
    merge_pdf = os.path.join(output_folder, 'maratona.pdf')
    merge_tutorial_pdf = os.path.join(output_folder, 'tutoriais.pdf')
    merge_pdfs(problem_pdf_l, merge_pdf)
    merge_pdfs(tutorial_pdf_l, merge_tutorial_pdf)
    for f in problem_pdf_l:
        os.remove(f)
    for f in tutorial_pdf_l:
        os.remove(f)
    if output_folder not in problem_folder_l:
        os.remove(os.path.join(output_folder, 'maratona.cls'))


def build_boca_packages(problem_folder_l: str, output_folder: str) -> None:
    """Builds BOCA packages from the list of problems"""
    info_log('Creating BOCA Files')
    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': False,
                   'problem_label': label}
        build_pdf(folder, folder, options)
        boca_pack(folder)
        boca_file_path = os.path.join(folder, 'boca.zip')
        boca_file = os.path.join(
            output_folder, os.path.basename(folder) + '-boca.zip')
        shutil.copy(boca_file_path, boca_file)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    for problem in args.problem_path:
        if (not os.path.exists(problem)):
            print(problem, "path doesn't exist.")
            sys.exit(1)
        if (not os.path.exists(os.path.join(problem, 'statement.md'))):
            print(problem, "path doesn't have an initialized problem.")
            sys.exit(1)
        if (args.mode == 'genpdf'):
            if (not os.path.exists(os.path.join(problem, 'input'))):
                print(problem, "path doesn't have an input folder.")
                sys.exit(1)
            if (not os.path.exists(os.path.join(problem, 'output'))):
                print(problem, "path doesn't have an output folder.")
                sys.exit(1)
        elif (args.mode == 'build' and not os.path.exists(os.path.join(problem, 'bin'))):
            command = ['python3', os.path.join(os.path.dirname(os.path.relpath(__file__)),
                                               'build.py'), 'build', problem]
            p = subprocess.run(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
            verify_command(p, "Error building problem.")

    os.makedirs(args.contest_folder, exist_ok=True)

    Paths.instance(args.problem_path, args.contest_folder)

    if (args.mode == 'build' and args.boca):
        build_boca_packages(args.problem_path, args.contest_folder)
        build_contest_pdf(args.problem_path, args.contest_folder)
        print("Contest build successfully.")
    elif (args.mode == 'build'):
        build_contest_pdf(args.problem_path, args.contest_folder)
        print("Contest build successfully.")
    elif (args.mode == 'genpdf'):
        build_contest_pdf(args.problem_path, args.contest_folder)
        print("PDFs generated successfully.")

