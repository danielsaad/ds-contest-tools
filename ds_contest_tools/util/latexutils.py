import os

from ds_contest_tools.enumarate.statement_files import StatementFiles

from .. import config
from ..core.latex_formatter import LatexFormatter
from .fileutils import has_lines
from .jsonutils import parse_json
from ..logger import info_log
from .utils import check_problem_metadata, verify_path

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
        formatter = LatexFormatter(
            f_out, problem_metadata, options, statement_folder)

        formatter.write_header()
        formatter.write_description()
        formatter.write_input()
        formatter.write_output()

        if interactive:
            formatter.write_interactor()

        # Print I/O examples
        in_list = get_io(input_folder, problem_metadata)
        out_list = get_io(output_folder, problem_metadata)

        formatter.write_examples(in_list, out_list)
        formatter.write_notes()
        formatter.write_footer()

    if has_lines(statement_folder, StatementFiles.TUTORIAL):
        tutorial_filename = os.path.basename(
            os.path.abspath(problem_folder)) + '-tutorial.tex'
        tutorial_filepath = os.path.join(problem_folder, tutorial_filename)
        info_log(f"Creating {tutorial_filename}")

        with open(tutorial_filepath, 'w') as f_out:
            LatexFormatter(f_out, problem_metadata, options,
                           statement_folder).write_tutorial()


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
