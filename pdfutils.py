import logging
import config
import glob
import subprocess
import os
import sys
from latexutils import clean_auxiliary_files, print_to_latex
from utils import verify_command


MERGE_TOOL = 'pdfjam'


def build_merge_command(pdf_list: list, output_file: str) -> list:
    command = [MERGE_TOOL]
    for f in pdf_list:
        command += [f]
    command += ['-o', output_file]
    return command


def merge_pdfs(pdf_list: list, output_file: str) -> None:
    logging.info(["Merging ", pdf_list])
    command = build_merge_command(pdf_list, output_file)
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    verify_command(p, "Error merging PDFs.")
    logging.info("PDFs Merged")


def build_pdf(problem_folder, output_directory='', options=config.DEFAULT_PDF_OPTIONS):
    logging.info('-Building PDF')
    md_list = glob.glob(os.path.join(problem_folder, '*.md'))
    filepath = md_list[0]
    if (not os.path.exists(filepath)):
        print("Statement file does not exists")
        sys.exit(1)
    print_to_latex(problem_folder, filepath, options)
    tex_filename = os.path.basename(os.path.abspath(problem_folder)) + '.tex'
    folder = problem_folder if output_directory == '' else output_directory
    tex_filepath = os.path.join(problem_folder, tex_filename)
    command = ["pdflatex", '--output-directory', folder, tex_filepath]
    p = subprocess.run(command, stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    verify_command(p, "Generation of problem file failed.")
    clean_auxiliary_files(folder)
    
    tutorial_filename = os.path.basename(
        os.path.abspath(problem_folder))+'-tutorial.tex'
    tutorial_filepath = os.path.join(
        problem_folder, tutorial_filename)
    if (os.path.isfile(tutorial_filepath)):
        command = ['pdflatex', '--output-directory', folder, tutorial_filepath]
        p = subprocess.run(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        verify_command(p, "Generation of tutorial file failed.")
        clean_auxiliary_files(folder)
