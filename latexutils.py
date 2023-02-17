import os
import io
import re
import sys
import config
from logger import info_log
from jsonutils import parse_json
from utils import verify_problem_json, verify_path
from fileutils import get_statement_files


def print_line(line: str, f_out: io.TextIOWrapper) -> None:
    """Prints 'line' on a file."""
    print(line, file=f_out, end='')


def multiple_replace(patterns: dict, text: str) -> str:
    """Replace key characters in patterns with their values."""
    regex = re.compile("(%s)" % "|".join(map(re.escape, patterns.keys())))
    return regex.sub(lambda mo: patterns[mo.string[mo.start():mo.end()]], text)


def get_io(io_folder: str, problem_metadata: dict) -> list:
    """Returns I/O lines for the examples of the PDF."""
    l = []
    io_samples = problem_metadata["io_samples"]
    interactive = problem_metadata['problem']['interactive']

    if (interactive):
        io_files = [os.path.join(io_folder, str(f)+'.interactive')
                    for f in range(1, io_samples+1)]
    else:
        io_files = [os.path.join(io_folder, str(f))
                    for f in range(1, io_samples+1)]
    for f in io_files:
        if (not os.path.isfile(f)):
            print(os.path.basename(f), 'file does not exist.')
            sys.exit(1)
        tc_io = []
        with open(f) as inf:
            for line in inf.readlines():
                tc_io.append(line.rstrip('\n'))
        l.append(tc_io)
    return l


def print_to_latex(problem_folder: str, options=config.DEFAULT_PDF_OPTIONS):
    """Generates '.tex' file of a problem."""
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    verify_problem_json(problem_metadata)

    statement_folder = os.path.join(problem_folder, 'statement')
    verify_path(statement_folder)

    interactive = problem_metadata['problem']['interactive']
    tex_filename = os.path.basename(os.path.abspath(problem_folder))+'.tex'
    tex_filepath = os.path.join(problem_folder, tex_filename)
    info_log(f"Creating {tex_filepath}")
    with open(tex_filepath, 'w') as f_out:
        print("\\documentclass{maratona}", file=f_out)
        print("\\begin{document}\n", file=f_out)
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
            for line in statement_lines:
                print_line(line, f_out)
        if (input_lines):
            print("\n\\Entrada\n", file=f_out)
            for line in input_lines:
                print_line(line, f_out)
        if (output_lines):
            print("\n\\Saida\n", file=f_out)
            for line in output_lines:
                print_line(line, f_out)
        if (interactive and interactor_lines):
            print("\n\\Interacao\n", file=f_out)
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
        info_log("Producing Tutorial")
        print_tutorial_to_latex(
            problem_folder, problem_metadata, tutorial_lines)


def print_tutorial_to_latex(problem_folder: str, problem_metadata: dict,
                            tutorial_lines: list) -> None:
    """Generates '-tutorial.tex' file of a problem."""
    tex_filepath = os.path.join(problem_folder, os.path.basename(
        os.path.abspath(problem_folder)) + '-tutorial.tex')
    info_log(f"Creating {tex_filepath}")
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


def clean_auxiliary_files(folder: str) -> None:
    """Remove files created after running the command 'pdflatex'."""
    files = [os.path.join(folder, x) for x in os.listdir(folder) if x.endswith(
        '.aux') or (x.endswith('.log') and not x == 'tool.log' and not
                    x == 'debug.log') or x.endswith('.out')]
    for f in files:
        os.remove(f)
