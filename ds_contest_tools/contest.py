import os
import shutil
import subprocess

from .boca import boca_pack
from .latexutils import clean_auxiliary_files
from .logger import info_log
from .metadata import Paths
from .pdfutils import build_pdf, merge_pdfs
from .utils import check_subprocess_output, convert_idx_to_string, verify_path


def build_contest_pdf(author: bool = False) -> None:
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
        options = {'display_author': author,
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


def build_boca_packages(author: bool = False) -> None:
    """Build BOCA packages from the list of problems."""
    info_log('Creating BOCA Files')
    problem_folder_l = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': author,
                   'problem_label': label,
                   'event': True}
        # Update PDF with new label and event
        build_pdf(folder, folder, options)
        boca_pack(folder, folder)
        boca_file_path = os.path.join(folder, 'boca.zip')
        boca_file = os.path.join(
            output_folder, os.path.basename(folder) + '-boca.zip')
        shutil.copy(boca_file_path, boca_file)


def build_input_output() -> None:
    """Copy problem input and output to the output folder."""
    problems_dir: list = Paths().get_problem_dir()
    output_dir: str = Paths().get_output_dir()
    for problem in problems_dir:
        info_log(
            f"Generating input/output files for problem {os.path.basename(problem)}")
        test_path = os.path.join(output_dir, os.path.basename(problem))
        test_path_input = os.path.join(test_path, 'input')
        test_path_output = os.path.join(test_path, 'output')
        os.makedirs(test_path, exist_ok=True)
        os.makedirs(test_path_input, exist_ok=True)
        os.makedirs(test_path_output, exist_ok=True)
        shutil.copytree(os.path.join(problem, 'input'),
                        test_path_input, dirs_exist_ok=True)
        shutil.copytree(os.path.join(problem, 'output'),
                        test_path_output, dirs_exist_ok=True)


def verify_problem(problem: str) -> None:
    """Check if the problem has the necessary files to create a BOCA package.
    If not, build the problem.
    
    Args:
        problem: Path to the problem folder.
    """
    verify_path(os.path.join(problem, 'statement'))

    input_dir = os.path.join(problem, 'input')
    output_dir = os.path.join(problem, 'output')
    checker_path = os.path.join(problem, 'bin', 'checker-boca')
    tool_directory = os.path.dirname(os.path.abspath(__file__))

    problem_name = os.path.basename(problem)
    if not os.path.exists(input_dir):
        info_log(f"Input folder not found. Building {problem_name} problem.")
    elif not os.path.exists(output_dir):
        info_log(f"Output folder not found. Building {problem_name} problem.")
    elif not os.path.exists(checker_path):
        info_log(f"BOCA checker not found. Building {problem_name} problem.")
    else:
        return

    command = ['python3', '-m',
               'ds_contest_tools.ds_contest_tools', 'build', problem]
    p = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(tool_directory))
    check_subprocess_output(p, f"Error building problem {problem_name}.")
