import os
import config
import sys
import logging
from jsonutils import parse_json


def print_line(line: str, f_out: str) -> None:
    """Prints 'line' on a file."""
    print(line, file=f_out, end='')


def get_io(io_folder: str, problem_metadata: dict) -> list:
    """Returns the input/output file lines of the examples in the pdf."""
    interactive = False
    if(problem_metadata['problem']['interactive']):
        interactive = True

    l = []
    io_samples = problem_metadata["io_samples"]

    if(interactive):
        io_files = [os.path.join(io_folder, str(f)+'.interactive')
                    for f in range(1, io_samples+1)]
    else:
        io_files = [os.path.join(io_folder, str(f))
                    for f in range(1, io_samples+1)]
    for f in io_files:
        if(not os.path.isfile(f)):
            print(f, 'file doest not exists.')
            sys.exit(1)
        tc_io = []
        with open(f) as inf:
            for line in inf.readlines():
                tc_io.append(line.rstrip('\n'))
        l.append(tc_io)
    return l


def print_to_latex(problem_folder, md_file, options=config.DEFAULT_PDF_OPTIONS):
    """Generates '.tex' file of a problem."""
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))

    # TODO: verify
    contest_metadata = parse_json(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'contest.json'))
    interactive = problem_metadata['problem']['interactive']

    tex_filename = os.path.basename(os.path.abspath(problem_folder))+'.tex'
    tex_filepath = os.path.join(problem_folder, tex_filename)
    logging.info("Creating " + tex_filepath)
    with open(md_file) as f_in, open(tex_filepath, 'w') as f_out:
        print("\\documentclass{maratona}", file=f_out)
        print("\\begin{document}\n", file=f_out)
        if(options['display_author']):
            print("\\begin{ProblemaAutor}{" + options['problem_label']
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}{" + problem_metadata["author"]["name"] + "}", file=f_out)
        else:
            print("\\begin{Problema}{" + options['problem_label']
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}", file=f_out)
        statement_lines = []
        input_lines = []
        output_lines = []
        note_lines = []
        tutorial_lines = []
        interactor_lines = []
        line = ""
        while(True):
            if(line.startswith('# Descrição')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    statement_lines.append(line)
            elif(line.startswith('# Entrada')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    input_lines.append(line)
            elif(line.startswith('# Saída')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    output_lines.append(line)
            elif(line.startswith('# Interação')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    interactor_lines.append(line)
            elif(line.startswith('# Notas')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    note_lines.append(line)
            elif(line.startswith('# Tutorial')):
                while(True):
                    line = f_in.readline()
                    if(line.startswith('# ') or not line):
                        break
                    tutorial_lines.append(line)
            else:
                line = f_in.readline()

            if(not line):
                break

        if(statement_lines):
            for line in statement_lines:
                print_line(line, f_out)
        if(input_lines):
            print("\\Entrada\n", file=f_out)
            for line in input_lines:
                print_line(line, f_out)
        if(output_lines):
            print("\\Saida\n", file=f_out)
            for line in output_lines:
                print_line(line, f_out)
        if(interactor_lines and interactive):
            print("\\Interacao\n", file=f_out)
            for line in interactor_lines:
                print_line(line, f_out)

        in_list = get_io(input_folder, problem_metadata)
        out_list = get_io(output_folder, problem_metadata)
        print("\n\n\\ExemploEntrada", file=f_out)
        print("\\begin{Exemplo}", file=f_out)
        for tc in range(0, len(in_list)):
            tc_input = in_list[tc]
            tc_output = out_list[tc]
            max_lines = max(len(tc_input), len(tc_output))
            for i in range(0, max_lines):
                # Escape # symbol
                if(tc % 2):
                    print('\\rowcolor{gray!20}', end='', file=f_out)
                if(i < len(tc_input)):
                    tc_input[i] = tc_input[i].replace('#', '\\#')
                    tc_input[i] = tc_input[i].replace('_', '\_')
                    tc_input[i] = tc_input[i].replace(' ', '~')
                    print('\\texttt{'+tc_input[i]+'}', end='', file=f_out)
                print(' & ', end='', file=f_out)
                if(i < len(tc_output)):
                    # Escape #
                    tc_output[i] = tc_output[i].replace('#', '\\#')
                    tc_output[i] = tc_output[i].replace('_', '\_')
                    tc_output[i] = tc_output[i].replace(' ', '~')
                    print('\\texttt{' + tc_output[i] + '}', end='', file=f_out)
                print('\\\\', file=f_out)
        print("\\end{Exemplo}\n", file=f_out)

        if(note_lines):
            print("\\Notas\n", file=f_out)
            for line in note_lines:
                print_line(line, f_out)

        if(options['display_author']):
            print("\\end{ProblemaAutor}", file=f_out)
        else:
            print("\\end{Problema}", file=f_out)
        print("\\end{document}", file=f_out)
    if(tutorial_lines):
        logging.info("Producing Tutorial")
        print_tutorial_to_latex(
            problem_folder, problem_metadata, tutorial_lines)


def print_tutorial_to_latex(problem_folder: str, problem_metadata: dict, 
                            tutorial_lines: list) -> None:
    """Generates '-tutorial.tex' file of a problem."""
    tex_filepath = os.path.join(problem_folder, os.path.basename(
        os.path.abspath(problem_folder)) + '-tutorial.tex')
    logging.info("Creating " +  tex_filepath)
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
        '.aux') or x.endswith('.log') or x.endswith('.out')]
    for f in files:
        os.remove(f)
