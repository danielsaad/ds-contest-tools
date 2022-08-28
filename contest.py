from operator import mod
from pdb import main
from pydoc import doc
from latexutils import clean_auxiliary_files
from pdfutils import build_pdf, merge_pdfs
import os

"""
Converts an integer to a string from alphabet [A-Z] using radix 26
"""


def convert_idx_to_string(idx):
    ans = ''
    while True:
        rem = mod(idx, 26)
        ans += chr(ord('A')+rem)
        idx //= 26
        if idx == 0:
            break
    return ans


"""
Builds a contest pdf from the PDFs from problem_folder_l
"""


def build_contest_pdf(problem_folder_l, output_folder):
    print('-Creating contest PDF')
    problem_pdf_l = []
    tutorial_pdf_l = []
    if not os.path.isdir(output_folder):
        print(output_folder, ' is not a valid directory')
        exit(1)

    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = {'display_author': False,
                   'problem_label': label}
        build_pdf(folder, output_folder, options)
        problem_pdf_l.append(os.path.join(output_folder, label+'.pdf'))
        tutorial_pdf_l.append(os.path.join(
            output_folder, label+'-tutorial.pdf'))
    clean_auxiliary_files(output_folder)
    merge_pdf = os.path.join(output_folder,'maratona.pdf')
    merge_tutorial_pdf = os.path.join(output_folder,'tutoriais.pdf')
    merge_pdfs(problem_pdf_l,merge_pdf)
    merge_pdfs(tutorial_pdf_l,merge_tutorial_pdf)
    for f in problem_pdf_l:
        os.remove(f)
    for f in tutorial_pdf_l:
        os.remove(f)
    

if __name__ == '__main__':
    pass
