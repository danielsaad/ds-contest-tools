from json import parse_json
from latexutils import print_to_latex
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


def build_pdf(problem_folder):
    print('-Building PDF')
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    md_list = glob.glob(os.path.join(problem_folder, '*.md'))
    filepath = md_list[0]
    if(not os.path.exists(filepath)):
        print("Statement file does not exists")
        sys.exit(1)
    print_to_latex(problem_folder, filepath)
    cwd = os.getcwd()
    os.chdir(problem_folder)
    p = subprocess.run(["pdflatex", problem_metadata["problem"]["label"]+".tex"],
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Generation of Problem file failed")
        sys.exit(1)

    tutorial_file = ('tutorial.tex')
    if(os.path.isfile(tutorial_file)):
        p = subprocess.run(["pdflatex", tutorial_file], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(p.returncode):
            print("Generation of Tutorial file failed")
            print(p.stdout, p.stderr)
            sys.exit(1)
    os.chdir(cwd)
