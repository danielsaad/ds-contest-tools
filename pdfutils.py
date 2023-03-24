import os
import subprocess
import sys

import config
from latexutils import clean_auxiliary_files, print_to_latex
from logger import info_log
from metadata import Paths
from utils import check_subprocess_output, verify_path

MERGE_TOOL = 'pdfjam'


def build_merge_command(pdf_list: list, output_file: str) -> list:
    """Returns the command to merge the PDFs."""
    command = [MERGE_TOOL]
    for f in pdf_list:
        command += [f]
    command += ['-o', output_file]
    return command


def merge_pdfs(pdf_list: list, output_file: str) -> None:
    """Creates contest PDF by merging all PDFs inside list."""
    pdfs = ''
    for pdf in pdf_list:
        pdfs += os.path.basename(pdf) + ' '
    info_log(f"Merging {pdfs}")
    command = build_merge_command(pdf_list, output_file)
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    check_subprocess_output(p, "Error merging PDFs.")
    info_log("PDFs Merged")


def build_pdf(problem_folder='', output_directory='', options=config.DEFAULT_PDF_OPTIONS) -> None:
    """Build problem and tutorial PDFs."""
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
