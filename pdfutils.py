from jsonutils import parse_json
from latexutils import clean_auxiliary_files, print_to_latex
import config
import glob
import subprocess
import os
import sys

MERGE_TOOL = 'pdfjam'


def build_merge_command(pdf_list, output_file):
    command = [MERGE_TOOL]
    for f in pdf_list:
        command += [f]
    command += ['-o', output_file]
    return command


def merge_pdfs(pdf_list, output_file):
    print('Merging', pdf_list)
    command = build_merge_command(pdf_list, output_file)
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("PDFs Merged")


def build_pdf(problem_folder, output_directory='', options=config.DEFAULT_PDF_OPTIONS):
    print('-Building PDF')
    md_list = glob.glob(os.path.join(problem_folder, '*.md'))
    filepath = md_list[0]
    if(not os.path.exists(filepath)):
        print("Statement file does not exists")
        sys.exit(1)
    print_to_latex(problem_folder, filepath, options)
    tex_filename = os.path.basename(os.path.abspath(problem_folder)) + '.tex'
    folder = problem_folder if output_directory == '' else output_directory
    tex_filepath = os.path.join(problem_folder, tex_filename)
    command = ["pdflatex", '--output-directory', folder, tex_filepath]
    p = subprocess.run(command, stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Generation of Problem file failed")
        sys.exit(1)
    clean_auxiliary_files(folder)

    tutorial_filename = os.path.basename(
        os.path.abspath(problem_folder))+'-tutorial.tex'
    tutorial_filepath = os.path.join(
        problem_folder, tutorial_filename)
    if(os.path.isfile(tutorial_filepath)):
        command = ['pdflatex', '--output-directory', folder, tutorial_filepath]
        p = subprocess.run(command, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(p.returncode):
            print("Generation of Tutorial file failed")
            print(p.stdout, p.stderr)
            sys.exit(1)
        clean_auxiliary_files(folder)
