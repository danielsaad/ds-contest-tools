import io
import os
import re

from .. import config
from ..core.factory.formatter_factory import FormatterFactory
from .fileutils import get_statement_files
from .jsonutils import parse_json
from ..logger import info_log
from .utils import check_problem_metadata, verify_path

from ds_contest_tools.core.tutorial_formatter import TutorialFormatter
from ds_contest_tools.core.contracts.latex_formatter_interface import LatexFormatter

def get_io(io_folder: str, problem_metadata: dict) -> list:
    """Return input/output examples for the problem from the given folder.

    Args:
        io_folder: The path to the directory containing the input/output files.
        problem_metadata: A dictionary containing metadata about the problem.

    Returns:
        A list of input/output examples to be used in the PDF.
    """
    l = []
    io_samples = problem_metadata["io_samples"]
    interactive = problem_metadata['problem']['interactive']

    if interactive:
        io_files = [os.path.join(io_folder, str(f)+'.interactive')
                    for f in range(1, io_samples+1)]
    else:
        io_files = [os.path.join(io_folder, str(f))
                    for f in range(1, io_samples+1)]
        
    for f in io_files:
        verify_path(f)
        tc_io = []
        with open(f) as inf:
            for line in inf.readlines():
                tc_io.append(line.rstrip('\n'))
        l.append(tc_io)
    return l


def print_to_latex(problem_folder: str, options=config.DEFAULT_PDF_OPTIONS):
    """Generates a '.tex' file of a problem from the given problem folder path.
    
    Args:
        problem_folder: The path of the problem folder.
        options: The dictionary with optional configuration for PDF file generation.
    """

    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)

    statement_folder = os.path.join(problem_folder, 'statement')
    verify_path(statement_folder)

    interactive = problem_metadata['problem']['interactive']
    tex_filename = os.path.basename(os.path.abspath(problem_folder))+'.tex'
    tex_filepath = os.path.join(problem_folder, tex_filename)
    info_log(f"Creating {os.path.basename(tex_filepath)}")

    with open(tex_filepath, 'w') as f_out:
        latex_class = options.get('latex_class', config.DEFAULT_LATEX_CLASS)

        formatter: LatexFormatter = FormatterFactory.get_formatter(latex_class)
        formatter.write_header(f_out, problem_metadata, options)

        # Get statement information
        statement_files = get_statement_files(statement_folder, interactive)
        with open(statement_files[0], 'r') as f:
            statement_lines = f.readlines()
        with open(statement_files[1], 'r') as f:
            input_lines = f.readlines()
        with open(statement_files[2], 'r') as f:
            output_lines = f.readlines()
        with open(statement_files[3], 'r') as f:
            note_lines = f.readlines()
        with open(statement_files[4], 'r') as f:
            tutorial_lines = f.readlines()
        interactor_lines = []
        if interactive:
            with open(statement_files[5], 'r') as f:
                interactor_lines = f.readlines()

        formatter.write_statement(f_out, statement_lines)
        formatter.write_io_formats(
            f_out, input_lines, output_lines, interactive, interactor_lines)

        # Print I/O examples
        in_list = get_io(input_folder, problem_metadata)
        out_list = get_io(output_folder, problem_metadata)

        formatter.write_examples(f_out, in_list, out_list)
        formatter.write_notes(f_out, note_lines)
        formatter.write_footer(f_out, options)
    if (tutorial_lines):
        info_log("Creating problem tutorial")
        tutorial_formatter = TutorialFormatter(problem_metadata)
        tutorial_formatter.build_tutorial(problem_folder, tutorial_lines)


def clean_auxiliary_files(folder: str, extensions: list = None) -> None:
    """Remove files with specified extensions from a given directory.

    Args:
        folder: The directory to clean up.
        extensions: A list of file extensions to remove.
    """
    if extensions is None:
        extensions = ['.aux', '.log', '.out']
    
    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in extensions and f not in ['tool.log', 'debug.log']:
                os.remove(os.path.join(root, f))
