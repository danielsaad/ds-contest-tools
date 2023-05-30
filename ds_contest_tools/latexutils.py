import io
import os
import re

from . import config
from .fileutils import get_statement_files
from .jsonutils import parse_json
from .logger import info_log
from .utils import check_problem_metadata, verify_path


def print_line(line: str, f_out: io.TextIOWrapper) -> None:
    """Writes a line to a file.

    Args:
        line: The line to be written to the file.
        f_out: The file to which the line will be written.
    """
    print(line, file=f_out, end='')


def multiple_replace(patterns: dict, text: str) -> str:
    """Performs multiple string replacements on a given text.

    This function replaces all occurrences of keys in the given `patterns`
    dictionary with their corresponding values in the given `text`.

    Args:
        patterns: A dictionary of patterns to be replaced in the text.
        text: The text on which to perform the replacements.

    Returns:
        The modified text with all the patterns replaced.
    """
    regex = re.compile("(%s)" % "|".join(map(re.escape, patterns.keys())))
    return regex.sub(lambda mo: patterns[mo.string[mo.start():mo.end()]], text)


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
            This dictionary contains the following keys:
            - display_author (bool): Whether to include the author's name in the problem description. Default is True.
            - problem_label (str): The label to identify the problem. Default is an empty string.
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
        print("\\documentclass{maratona}", file=f_out)
        print("\\begin{document}", file=f_out)
        if options['event']:
            print("\\lhead{" + problem_metadata['problem']['event'] + "}\n", file=f_out)
        if (options['display_author']):
            print("\\begin{ProblemaAutor}{" + options['problem_label']
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}{" + problem_metadata["author"]["name"] + "}\n", file=f_out)
        else:
            print("\\begin{Problema}{" + options['problem_label']
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}\n", file=f_out)

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

        # Print statement information
        if (statement_lines):
            statement_lines[-1] = statement_lines[-1].rstrip()
            for line in statement_lines:
                print_line(line, f_out)
        if (input_lines):
            print("\n\n\\Entrada\n", file=f_out)
            input_lines[-1] = input_lines[-1].rstrip()
            for line in input_lines:
                print_line(line, f_out)
        if (output_lines):
            print("\n\n\\Saida\n", file=f_out)
            output_lines[-1] = output_lines[-1].rstrip()
            for line in output_lines:
                print_line(line, f_out)
        if (interactive and interactor_lines):
            print("\n\n\\Interacao\n", file=f_out)
            for line in interactor_lines:
                print_line(line, f_out)

        # Print I/O examples
        in_list = get_io(input_folder, problem_metadata)
        out_list = get_io(output_folder, problem_metadata)
        patterns = {"#": "\\#",
                    "$": "\\$",
                    "%": "\\%",
                    "&": "\\&",
                    "_": "\\_",
                    "{": "\\{",
                    "}": "\\}",
                    ">": "\\textless{}",
                    "<": "\\textgreater{}",
                    "^": "\\textasciicircum{}",
                    "\\": "\\textbackslash{}",
                    " ": "~"}
        print("\n\n\\ExemploEntrada", file=f_out)
        print("\\begin{Exemplo}", file=f_out)
        for tc in range(0, len(in_list)):
            tc_input = in_list[tc]
            tc_output = out_list[tc]
            max_lines = max(len(tc_input), len(tc_output))
            for i in range(0, max_lines):
                if (tc % 2):
                    print('\\rowcolor{gray!20}', end='', file=f_out)
                if (i < len(tc_input)):
                    print('\\texttt{'+multiple_replace(patterns, tc_input[i])+'}',
                          end='', file=f_out)
                print(' & ', end='', file=f_out)
                if (i < len(tc_output)):
                    print('\\texttt{'+multiple_replace(patterns, tc_output[i])+'}',
                          end='', file=f_out)
                print('\\\\', file=f_out)
        print("\\end{Exemplo}\n", file=f_out)

        if (note_lines):
            print("\\Notas\n", file=f_out)
            for line in note_lines:
                print_line(line, f_out)

        if (options['display_author']):
            print("\\end{ProblemaAutor}", file=f_out)
        else:
            print("\\end{Problema}", file=f_out)
        print("\\end{document}", file=f_out)
    if (tutorial_lines):
        info_log("Creating problem tutorial")
        print_tutorial_to_latex(
            problem_folder, problem_metadata, tutorial_lines)


def print_tutorial_to_latex(problem_folder: str, problem_metadata: dict,
                            tutorial_lines: list) -> None:
    """Generates the LaTeX file for the tutorial of a problem.

    Args:
        problem_folder: The path to the problem directory.
        problem_metadata: The dictionary containing the problem metadata.
        tutorial_lines: A list of strings containing the tutorial lines.
    """
    tex_filepath = os.path.join(problem_folder, os.path.basename(
        os.path.abspath(problem_folder)) + '-tutorial.tex')
    info_log(f"Creating {os.path.basename(tex_filepath)}")
    with open(tex_filepath, 'w') as f_out:
        print("\\documentclass[10pt]{article}", file=f_out)
        print("\\usepackage[utf8]{inputenc}", file=f_out)
        print("\\usepackage{amsmath,amsthm,amssymb}", file=f_out)
        print("\\usepackage{fullpage}", file=f_out)
        print("\\usepackage{url}", file=f_out)
        print("\\pagenumbering{gobble}", file=f_out)
        print("\\title{ Tutorial: " +
              problem_metadata["problem"]["title"]+"}", file=f_out)
        print("\\author{"+problem_metadata["author"]["name"]+"}", file=f_out)
        print("\\date{}", file=f_out)
        print("\\begin{document}", file=f_out)
        print("\\maketitle", file=f_out)
        for line in tutorial_lines:
            print_line(line, f_out)
        print("\\end{document}", file=f_out)


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
