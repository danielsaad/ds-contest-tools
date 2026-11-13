import os
import shutil
import subprocess

from .boca import boca_pack
from . import config
from .util.latexutils import clean_auxiliary_files
from .logger import info_log, muted_info_log
from .metadata import Paths
from .util.pdfutils import build_pdf, merge_pdfs
from .util.utils import check_subprocess_output, convert_idx_to_string, verify_path


def contest_pdf_options(label: str, author: bool, latex_class: str, event: bool = True, page_numbers: bool = False) -> dict:
    """Return the PDF options of a contest problem.

    Starts from `config.DEFAULT_PDF_OPTIONS`, so `build` and `contest` share
    the same defaults. `author` (the `--author` flag) only forces the author
    to be shown; it never hides it. `event` is turned off by `--no-event`.
    `page_numbers` is turned on by `--page-numbers`.
    """
    options = config.DEFAULT_PDF_OPTIONS.copy()
    options.update({'display_author': options['display_author'] or author,
                    'problem_label': label,
                    'event': event,
                    'page_numbers': page_numbers,
                    'latex_class': latex_class})
    return options


def page_ranges(page_counts: list) -> list:
    """Return (first page, total pages) for each document of a merged PDF."""
    total_pages = sum(page_counts)
    ranges = []
    first_page = 1
    for count in page_counts:
        ranges.append((first_page, total_pages))
        first_page += count
    return ranges


def build_contest_pdf(author: bool = False, latex_class: str = config.DEFAULT_LATEX_CLASS, event: bool = True, page_numbers: bool = False) -> None:
    """Build contest PDF from PDFs of the list of problems."""
    info_log('Creating contest PDF')

    problem_pdf_l = []
    tutorial_pdf_l = []
    problem_folder_l = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()

    from .util.pdfutils import copy_latex_assets, remove_latex_assets
    copied_assets = copy_latex_assets(latex_class, output_folder)
    try:
        labels = [convert_idx_to_string(i) for i in range(len(problem_folder_l))]
        statement_ranges = tutorial_ranges = [None] * len(problem_folder_l)
        if page_numbers:
            # Primeira passada: só conta as páginas de cada problema.
            statement_counts, tutorial_counts = [], []
            with muted_info_log():
                for label, folder in zip(labels, problem_folder_l):
                    options = contest_pdf_options(label, author, latex_class, event, page_numbers)
                    statement_pages, tutorial_pages = build_pdf(folder, output_folder, options)
                    basename = os.path.basename(folder)
                    merged = os.path.exists(os.path.join(folder, basename+'-tutorial.pdf'))
                    statement_counts.append(statement_pages)
                    tutorial_counts.append(tutorial_pages if merged else 0)
            statement_ranges = page_ranges(statement_counts)
            tutorial_ranges = page_ranges(tutorial_counts)

        for i, folder in enumerate(problem_folder_l):
            options = contest_pdf_options(labels[i], author, latex_class, event, page_numbers)
            options['pagination'] = statement_ranges[i]
            options['tutorial_pagination'] = tutorial_ranges[i]
            build_pdf(folder, output_folder, options)
            basename = os.path.basename(folder)
            problem_pdf_l.append(os.path.join(output_folder, basename+'.pdf'))
            if os.path.exists(os.path.join(folder, basename+'-tutorial.pdf')):
                tutorial_pdf_l.append(os.path.join(
                    output_folder, basename+'-tutorial.pdf'))
        clean_auxiliary_files(output_folder)
        merge_pdf = os.path.join(output_folder, 'maratona.pdf')
        merge_tutorial_pdf = os.path.join(output_folder, 'tutoriais.pdf')
        merge_pdfs(problem_pdf_l, merge_pdf)
        if tutorial_pdf_l:
            merge_pdfs(tutorial_pdf_l, merge_tutorial_pdf)
        for f in problem_pdf_l:
            folder_name = os.path.basename(output_folder) + '.pdf'
            if folder_name != os.path.basename(f):
                os.remove(f)
        for f in tutorial_pdf_l:
            folder_name = os.path.basename(output_folder) + '-tutorial.pdf'
            if folder_name != os.path.basename(f):
                os.remove(f)
    finally:
        remove_latex_assets(copied_assets)


def build_boca_packages(author: bool = False, latex_class: str = config.DEFAULT_LATEX_CLASS, event: bool = True, page_numbers: bool = False) -> None:
    """Build BOCA packages from the list of problems."""
    info_log('Creating BOCA Files')
    problem_folder_l = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    for i, folder in enumerate(problem_folder_l):
        label = convert_idx_to_string(i)
        options = contest_pdf_options(label, author, latex_class, event, page_numbers)
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
