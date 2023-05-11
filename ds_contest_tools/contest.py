import argparse
import os
import shutil
import subprocess

from .boca import boca_pack
from .latexutils import clean_auxiliary_files
from .logger import info_log
from .metadata import Paths
from .pdfutils import build_pdf, merge_pdfs
from .utils import (check_subprocess_output, convert_idx_to_string,
                    instance_paths, verify_path)


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--boca', action='store_true',
                        default=False, help='build contest in BOCA format.')
    parser.add_argument('mode', choices=['build', 'genpdf', 'genio'],
                        help='build: build problems and create contest PDFs.\n' +
                        'genpdf: generates problem and tutorial PDFs.\n'
                        'genio: generates problem input and output files.')
    parser.add_argument('problem_path', help='path to the problem.',
                        nargs='+')
    parser.add_argument(
        'contest_folder', help='directory which the contest will be saved.')
    return parser


def build_contest_pdf() -> None:
    """Build contest PDF from PDFs of the list of problems."""
    info_log('Creating contest PDF')

    problem_pdf_l = []
    tutorial_pdf_l = []
    problem_folder_l = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()

    cls_file = os.path.join(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'files'), 'maratona.cls')
    shutil.copy(cls_file, output_folder)
    # Generate problems PDFs
    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': False,
                   'problem_label': label,
                   'event': True}
        build_pdf(folder, output_folder, options)
        basename = os.path.basename(folder)
        problem_pdf_l.append(os.path.join(output_folder, basename+'.pdf'))
        if os.path.exists(os.path.join(folder, basename+'-tutorial.pdf')):
            tutorial_pdf_l.append(os.path.join(
                output_folder, basename+'-tutorial.pdf'))
    # Merge PDFs
    clean_auxiliary_files(output_folder)
    merge_pdf = os.path.join(output_folder, 'maratona.pdf')
    merge_tutorial_pdf = os.path.join(output_folder, 'tutoriais.pdf')
    merge_pdfs(problem_pdf_l, merge_pdf)
    if (tutorial_pdf_l):
        merge_pdfs(tutorial_pdf_l, merge_tutorial_pdf)
    # Remove problems PDFs and ignore PDFs which are from
    # the same folder as the contest.
    for f in problem_pdf_l:
        folder_name = os.path.basename(output_folder) + '.pdf'
        if folder_name != os.path.basename(f):
            os.remove(f)
    for f in tutorial_pdf_l:
        folder_name = os.path.basename(output_folder) + '-tutorial.pdf'
        if folder_name != os.path.basename(f):
            os.remove(f)
    if output_folder not in problem_folder_l:
        os.remove(os.path.join(output_folder, 'maratona.cls'))


def build_boca_packages() -> None:
    """Build BOCA packages from the list of problems."""
    info_log('Creating BOCA Files')
    problem_folder_l = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': False,
                   'problem_label': label,
                   'event': True}
        # Update PDF with new label and event
        build_pdf(folder, folder, options)
        boca_pack(folder)
        boca_file_path = os.path.join(folder, 'boca.zip')
        boca_file = os.path.join(
            output_folder, os.path.basename(folder) + '-boca.zip')
        shutil.copy(boca_file_path, boca_file)


def build_input_output() -> None:
    """Copy problem input and output to the output folder.
    """
    problems_dir: list = Paths().get_problem_dir()
    output_dir: str = Paths().get_output_dir()
    for problem in problems_dir:
        info_log(f"Generating I/O files for problem {os.path.basename(problem)}")
        test_path = os.path.join(output_dir, os.path.basename(problem))
        test_path_input = os.path.join(test_path, 'input')
        test_path_output = os.path.join(test_path, 'output')
        os.makedirs(test_path, exist_ok=True)
        os.makedirs(test_path_input, exist_ok=True)
        os.makedirs(test_path_output, exist_ok=True)
        shutil.copytree(os.path.join(problem, 'input'), test_path_input, dirs_exist_ok=True)
        shutil.copytree(os.path.join(problem, 'output'), test_path_output, dirs_exist_ok=True)


def verify_problem(problem: str, mode: str, boca: bool) -> None:
    """Check if the problem is ready to be used"""
    verify_path(problem)
    verify_path(os.path.join(problem, 'statement'))
    verify_path(os.path.join(problem, 'input'))
    verify_path(os.path.join(problem, 'output'))

    if mode == 'genpdf' or mode == 'genio':
        return

    tool_directory = os.path.dirname(os.path.abspath(__file__))
    checker_path = os.path.join(problem, 'bin', 'checker-boca')
    # Verify if the checker-boca exists
    if boca and not os.path.exists(checker_path):
        info_log(f"BOCA checker not found. Building {problem} problem.")
        command = ['python3', os.path.join(
            tool_directory, 'build.py'), 'build', problem]
        p = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check_subprocess_output(p, f"Error building problem {problem}.")


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    instance_paths(args.problem_path, args.contest_folder)
    for problem in args.problem_path:
        verify_problem(problem, args.mode, args.boca)
    os.makedirs(args.contest_folder, exist_ok=True)

    if args.mode == 'genio':
        build_input_output()
    elif (args.mode == 'build' and args.boca):
        build_boca_packages()
        build_contest_pdf()
        info_log("Contest build successfully.")
    elif (args.mode == 'build'):
        build_contest_pdf()
        info_log("Contest build successfully.")
    elif (args.mode == 'genpdf'):
        build_contest_pdf()
        info_log("PDFs generated successfully.")
