import os
import subprocess
from typing import Optional

import config
from latexutils import clean_auxiliary_files, print_to_latex
from logger import info_log
from metadata import Paths
from utils import check_subprocess_output, verify_path

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
                       stderr=subprocess.PIPE, text=True)
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
    command = ["pdflatex", '--output-directory', folder, tex_filepath]
    p = subprocess.run(command, stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    check_subprocess_output(p, "Generation of problem file failed.")
    clean_auxiliary_files(folder)

    # Generate tutorial PDF from tex file
    tutorial_filename = os.path.basename(problem_folder)+'-tutorial.tex'
    tutorial_filepath = os.path.join(problem_folder, tutorial_filename)
    if os.path.isfile(tutorial_filepath):
        command = ['pdflatex', '--output-directory', folder, tutorial_filepath]
        p = subprocess.run(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        check_subprocess_output(p, "Generation of tutorial file failed.")
        clean_auxiliary_files(folder)
