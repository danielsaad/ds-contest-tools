import os
import subprocess
import sys
from typing import Optional

from . import config
from .latexutils import clean_auxiliary_files, print_to_latex
from .logger import info_log
from .metadata import Paths
from .utils import check_subprocess_output, verify_path

MERGE_TOOL = 'pdfjam'


def build_merge_command(pdf_list: list, output_file: str) -> list:
    """Constructs a command to merge a list of PDF files into a single output file.

    Args:
        pdf_list: A list of strings representing the paths to the PDF files to be merged.
        output_file: A string representing the path to the output file to be generated.

    Returns:
        A list of strings representing the command to merge the PDF files.

    """
    command: list = [MERGE_TOOL]
    for f in pdf_list:
        command += [f]
    command += ['-o', output_file]
    return command


def merge_pdfs(pdf_list: list, output_file: str) -> None:
    """Merges multiple PDF files into a single PDF file.

    Args:
        pdf_list: A list of strings representing the paths to the PDF files to be merged.
        output_file: A string representing the path to the output file to be generated.
    """
    pdfs: str = ' '.join(os.path.basename(pdf) for pdf in pdf_list)
    info_log(f"Merging {pdfs}")

    command: list = build_merge_command(pdf_list, output_file)
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    check_subprocess_output(p, "Error merging PDFs.")
    info_log("PDFs Merged")


def build_pdf(problem_folder: Optional[str] = '', output_directory: Optional[str] = '', options=config.DEFAULT_PDF_OPTIONS) -> None:
    """Builds the problem and tutorial PDFs.

    Problem folder and output directory are optional due to the creation of contests PDFs.

    Args:
        problem_folder: The path to the problem folder. If empty, the default problem folder is used.
        output_directory: The path to the output directory. If empty, the default problem folder is used.
        options: A dictionary containing the options to pass to the LaTeX compiler.
    """
    info_log('Building PDF')
    if problem_folder == '':
        problem_folder = Paths().get_problem_dir()
    verify_path(os.path.join(problem_folder, 'maratona.cls'))

    # Generate PDF from tex file
    print_to_latex(problem_folder, options)
    folder = problem_folder if output_directory == '' else output_directory

    tex_filename = os.path.basename(problem_folder) + '.tex'
    tex_filepath = os.path.join(problem_folder, tex_filename)
    generate_pdf(problem_folder, folder, tex_filepath)

    # Generate tutorial PDF from tex file
    tutorial_filename = os.path.basename(problem_folder)+'-tutorial.tex'
    tutorial_filepath = os.path.join(problem_folder, tutorial_filename)
    if os.path.isfile(tutorial_filepath):
        generate_pdf(problem_folder, folder, tutorial_filepath)


def generate_pdf(problem_folder: str, output_folder: str, tex_path: str) -> None:
    """Generates a PDF from a tex file.

    Args:
        output_folder: The path to the output folder.
        tex_path: The path to the tex file.
    """
    old_cwd = os.getcwd()
    command = ["pdflatex", '--output-directory',
               output_folder, '-interaction=nonstopmode', tex_path]

    os.chdir(problem_folder)
    try:
        p = subprocess.run(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=10)
    except subprocess.TimeoutExpired:
        info_log("Timeout error while generating pdf. Maybe a package is missing?")
        sys.exit(0)
    os.chdir(old_cwd)

    check_subprocess_output(p, "Generation of problem file failed.")
    clean_auxiliary_files(output_folder)
