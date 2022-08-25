#!/usr/bin/python3

# TODO: clean temporary files


import sys
import os
import subprocess
import glob
import shutil
import re
import errno
import json
import argparse


def custom_key(str):
    return +len(str), str.lower()


def parse_json(json_file):
    print(os.getcwd())
    json_data = {}

    if(not os.path.isfile(json_file)):
        print(json_file, 'does not exists.')
        sys.exit(1)

    with open(json_file) as f:
        json_data = json.load(f)
    return json_data


class default_boca_limits:
    time_limit = 1  # time limit for all tests
    number_of_repetitions = 1  # number of repetitions
    maximum_memory = 512  # Maximum memory size (MB)
    maximum_output_size = 4096  # Maximum output size (KB)


def boca_zip(boca_folder):
    old_cwd = os.getcwd()
    os.chdir(boca_folder)
    zip_filename = os.path.basename(boca_folder)+'.zip'
    subprocess.run('zip'+' -r ' + zip_filename + ' . ', shell=True)
    os.rename(zip_filename, os.path.join('..', zip_filename))
    os.chdir(old_cwd)


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)


def copy_directory(source, dest):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
            if(dirs and files):
                shutil.copyfile(os.path.join(root, file),
                                os.path.join(dest_path, file))


class statement_metadata:
    def __init__(self, problem_id='', title='', timelimit=0, author=''):
        self.problem_id = problem_id
        self.title = title
        self.timelimit = timelimit
        self.author = author


def parse_yaml(f):
    # read the first ---
    line = f.readline()
    d = {}
    while(True):
        line = f.readline().rstrip()
        if('---' in line):
            break
        lhs = line.split(": ")[0]
        rhs = line.split(": ")[1]
        rhs = rhs.strip('\"')
        d[lhs] = rhs
    smd = statement_metadata(
        d['problem_id'], d['title'], int(d['timelimit']), d['author'])
    return smd


def get_io(io_folder, problem_metadata):
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


def print_line(line, f_out):
    # line = re.sub(r'\*\*(.+)\*\*', r'\\textbf{\1}', line)
    # line = re.sub(r'\*(.+)\*', r'\\textit{\1}', line)
    print(line, file=f_out, end='')


def print_tutorial_to_latex(problem_folder, problem_metadata, tutorial_lines):
    with open(os.path.join(problem_folder, 'tutorial.tex'), 'w') as f_out:
        # TODO: use tutorial specific class
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
# Parse the markdown file to a .tex file


def print_to_latex(problem_folder, md_file):

    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))

    # TODO: verify
    contest_metadata =  parse_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contest.json'))
    interactive = problem_metadata['problem']['interactive']

    with open(md_file) as f_in, open(os.path.join(os.path.dirname(md_file), problem_metadata["problem"]["label"]+'.tex'), 'w') as f_out:
        print("\\documentclass{maratona}", file=f_out)
        print("\\begin{document}\n", file=f_out)
        if(contest_metadata['include_author'] == True):
            print("\\begin{ProblemaAutor}{" + problem_metadata["problem"]["label"]
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}{" + problem_metadata["author"]["name"] + "}", file=f_out)
        else:
            print("\\begin{Problema}{" + problem_metadata["problem"]["label"]
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

        if(contest_metadata['include_author']):
            print("\\end{ProblemaAutor}", file=f_out)
        else:
            print("\\end{Problema}", file=f_out)
        print("\\end{document}", file=f_out)
    if(tutorial_lines):
        print("-Producing Tutorial")
        print_tutorial_to_latex(
            problem_folder, problem_metadata, tutorial_lines)

# Builds a pdf file from a markdown


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


def build_executables(problem_folder):
    build_folder = os.path.join(problem_folder, 'build')
    build_debug_folder = os.path.join(problem_folder, 'build_debug')
    os.makedirs(build_folder, exist_ok=True)
    os.makedirs(build_debug_folder, exist_ok=True)

    # store cwd
    old_cwd = os.getcwd()

    # change cwd to build folder
    os.chdir(build_debug_folder)

    # run cmake and install executables
    print("-Compiling debug executables")
    p = subprocess.run(['cmake', '..', '-DCMAKE_BUILD_TYPE=DEBUG'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("CMAKE failed.")
        sys.exit(1)
    p = subprocess.run(
        ['make', '-j'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Compilation failed.")
        sys.exit(1)
    p = subprocess.run(['make', 'install'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Binaries instalation failed.")
        sys.exit(1)

    # run cmake and install executables

    # restore cwd
    os.chdir(old_cwd)
    # change cwd to build folder
    os.chdir(build_folder)
    # run cmake and install executables
    print("-Compiling release executables")
    p = subprocess.run(['cmake', '..', '-DCMAKE_BUILD_TYPE=RELEASE'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("CMAKE failed.")
        sys.exit(1)
    p = subprocess.run(
        ['make', '-j'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Compilation failed.")
        sys.exit(1)
    p = subprocess.run(['make', 'install'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Binaries instalation failed.")
        sys.exit(1)
    # restore cwd
    os.chdir(old_cwd)


def run_programs(problem_folder):
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    # Generate input and output folders
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    # store old cwd
    old_cwd = os.getcwd()

    # change cwd to input folder
    os.chdir(input_folder)
    # run generator
    generator_path = os.path.join('../bin', 'generator')
    print('-Generating inputs')
    subprocess.run(generator_path)

    # Run validator on generated inputs, exclude interactive IO
    input_files = [f for f in os.listdir() if os.path.isfile(f)
                   and not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    for fname in input_files:
        with open(fname) as f:
            p = subprocess.Popen([os.path.join('../bin', 'validator')], stdin=f, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()
            if(out or err):
                print("Failed validation on input", fname)
                exit(1)

    print("-Producing outputs")
    # change cwd to output folder
    os.chdir(old_cwd)
    os.chdir(output_folder)
    # Run ac solution on inputs to produce outputs
    for fname in input_files:
        inf_path = os.path.join('../input', fname)
        ouf_path = fname
        with open(os.path.join('../input', fname), 'r') as inf, open(fname, 'w') as ouf:
            ac_solution = os.path.join('../bin', 'ac')
            if(problem_metadata["problem"]["interactive"]):
                interactor = os.path.join('../bin/interactor')
                # TODO: do this in a more pythonic way
                if(os.path.isfile('tmpfifo')):
                    print("Removing existant FIFO")
                    subprocess.run(['rm', 'tmpfifo'])
                subprocess.run(['mkfifo', 'tmpfifo'])
                command = interactor + ' ' + inf_path + ' ' + ouf_path + \
                    ' < tmpfifo | ' + ac_solution + ' > tmpfifo'
                p = subprocess.run(command, stderr=subprocess.PIPE, shell=True)
                subprocess.run(['rm', 'tmpfifo'])

            else:
                p = subprocess.Popen([ac_solution], stdin=inf, stdout=ouf)
                _, err = p.communicate()
            if(p.returncode):
                print("Generation of output for input", fname, 'failed')
                sys.exit(1)
    os.chdir(old_cwd)


def build(problem_folder):
    build_executables(problem_folder)
    run_programs(problem_folder)
    build_pdf(problem_folder)


def merge_pdfs():
    # Remove merge pdf file if already existed
    if(os.path.exists('Maratona/Maratona.pdf')):
        os.remove('Maratona/Maratona.pdf')

    print("Merging PDFs")
    old_cwd = os.getcwd()
    os.chdir('Maratona')
    subprocess.run(['pdflatex', 'Capa.tex'],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.chdir(old_cwd)
    pdfs_all = [os.path.join('Maratona', f) for f in os.listdir('Maratona')]
    pdfs = sorted([f for f in pdfs_all if f.endswith(
        '.pdf') if f != 'Maratona/Capa.pdf' and f != 'Maratona/Tutoriais.pdf' and not f.startswith('Maratona/tutorial-')])
    command = ['pdfjam', 'Maratona/Capa.pdf']
    tutorials = sorted([f for f in pdfs_all if f.endswith(
        '.pdf') if f != 'Maratona/Capa.pdf' and f.startswith('Maratona/tutorial-')])
    command = ['pdfjam', 'Maratona/Capa.pdf']
    command_tutorial = ['pdfjam']
    for f in pdfs:
        command += [f]
    for f in tutorials:
        command_tutorial += [f]
    command += ['-o', 'Maratona/Maratona.pdf']
    command_tutorial += ['-o', 'Maratona/Tutoriais.pdf']
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("PDFs Merged")
    subprocess.run(command_tutorial, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)
    print("Tutorials Merged")


def build_all():
    problem_ids = [f for f in os.listdir(
        'Problemas') if os.path.isdir(os.path.join('Problemas', f))]
    for id in problem_ids:
        build(id)
    merge_pdfs()

# Create the structure for the folder of a problem


def init(problem_folder, interactive=False):
    folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'arquivos')
    shutil.copytree(folder, problem_folder, ignore=shutil.ignore_patterns('boca'))
    # Rename files and folders if the problem is interactive
    interactive_statement = os.path.join(
        problem_folder, 'statement-interactive.md')
    interactor = os.path.join(*[problem_folder, 'src','interactor.cpp'])
    interactive_json = os.path.join(problem_folder, 'problem-interactive.json')
    if(interactive):
        shutil.move(interactive_statement, os.path.join(
            problem_folder, 'statement.md'))
        shutil.move(interactive_json, os.path.join(
            problem_folder, 'problem.json'))
    else:
        os.remove(interactive_statement)
        os.remove(interactive_json)
        os.remove(interactor)


def pack2boca(problem_folder):
    build(problem_folder)
    # Create Boca folder
    boca_template_folder = os.path.join(
        *[os.path.dirname(os.path.abspath(__file__)), 'arquivos', 'boca'])
    boca_folder = os.path.join(*[problem_folder,'boca'])
    # Copy template files
    recursive_overwrite(boca_template_folder, boca_folder)
    # Get problem metadata
    problem_md = glob.glob(os.path.join(problem_folder, '*.md'))[0]
    tl = 0
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    # with open(problem_md) as f:
    #     # Compile, Run and Tests Remains the Same

    #     # Description
    boca_description_folder = os.path.join(boca_folder, 'description')
    with open(os.path.join(boca_description_folder, 'problem.info'), 'w+') as f:
        f.write('basename='+problem_metadata['problem']['label']+'\n')
        f.write('fullname='+problem_metadata['problem']['label']+'\n')
        f.write('descfile='+problem_metadata['problem']['label']+'.pdf\n')

    pdf_file = os.path.join(
        problem_folder, problem_metadata['problem']['label']+'.pdf')
    shutil.copy2(pdf_file, boca_description_folder)

    # Compare
    shutil.copy2(os.path.join(
        *[problem_folder, 'bin', 'checker-boca']), os.path.join(boca_folder, 'compare'))
    shutil.copy2(os.path.join(*[boca_folder, 'compare', 'checker-boca']),
                 os.path.join(*[boca_folder, 'compare', 'c']))
    shutil.copy2(os.path.join(*[boca_folder, 'compare', 'checker-boca']),
                 os.path.join(*[boca_folder, 'compare', 'cpp']))
    shutil.copy2(os.path.join(*[boca_folder, 'compare', 'checker-boca']),
                 os.path.join(*[boca_folder, 'compare', 'java']))
    shutil.copy2(os.path.join(*[boca_folder, 'compare', 'checker-boca']),
                 os.path.join(*[boca_folder, 'compare', 'py2']))
    shutil.copy2(os.path.join(*[boca_folder, 'compare', 'checker-boca']),
                 os.path.join(*[boca_folder, 'compare', 'py3']))
    # Limits

    java_python_time_factor = 3
    for filename in os.listdir(os.path.join(boca_template_folder, 'limits')):
        with open(os.path.join(*[boca_folder, 'limits', filename]), 'w+') as f:
            tl = problem_metadata['problem']['time_limit']
            if(filename in ['java', 'py2', 'py3']):
                tl = problem_metadata['problem']['time_limit'] * \
                    java_python_time_factor
            f.write('echo ' + str(tl) + '\n')
            f.write('echo ' + str(default_boca_limits.number_of_repetitions)+'\n')
            f.write('echo ' + str(default_boca_limits.maximum_memory)+'\n')
            f.write('echo ' + str(default_boca_limits.maximum_output_size)+'\n')
            f.write('exit 0\n')

    # Input
    boca_input_folder = os.path.join(boca_folder, 'input')
    problem_input_folder = os.path.join(problem_folder, 'input')
    os.makedirs(boca_input_folder, exist_ok=True)
    input_files = [os.path.join(problem_input_folder, f) for
                   f in os.listdir(problem_input_folder) if os.path.isfile(os.path.join(problem_input_folder, f))]
    print('input_files = ', ' '.join(input_files))
    for filename in input_files:
        shutil.copy2(filename, boca_input_folder)

    # Output
    boca_output_folder = os.path.join(boca_folder, 'output')
    problem_output_folder = os.path.join(problem_folder, 'output')
    os.makedirs(boca_output_folder, exist_ok=True)
    output_files = [os.path.join(problem_output_folder, f) for
                    f in os.listdir(problem_output_folder) if os.path.isfile(os.path.join(problem_output_folder, f))]
    print('output_files = ', ' '.join(output_files))
    for filename in output_files:
        shutil.copy2(filename, boca_output_folder)
    boca_zip(boca_folder)


def packall2boca():
    problem_ids = [f for f in os.listdir(
        'Problemas') if os.path.isdir(os.path.join('Problemas', f))]
    for id in problem_ids:
        pack2boca(id)


def pack2uri(problem_id):
    print('Not implemented')
    pass


def packall2uri():
    print('Not implemented')
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
                        default=False, help='apply action on all problems')
    parser.add_argument('-i', '--interactive', action='store_true',
                        default=False, help='set problem do interative on init')
    parser.add_argument(
        'mode', choices=['init', 'build', 'buildall', 'pack2boca', 'packall2boca'], help='\ninit: init a problem\nbuild: build  a problem.\npack2boca: pack a problem to BOCA format.\n')
    parser.add_argument('problem_id', nargs='?')
    args = parser.parse_args()
    if(not args.all and not args.problem_id):
        parser.error(args.mode + ' mode requires a problem id. Usage:' +
                     sys.argv[0] + ' ' + args.mode + ' <problem ID>')
    if(args.mode == 'init'):
        print('Initializing problem', args.problem_id)
        init(args.problem_id, args.interactive)
        print('Problem', args.problem_id, 'initialized')
    elif(args.mode == 'build'):
        if(not args.all):
            print("Building problem", args.problem_id)
            build(args.problem_id)
        else:
            build_all()
    elif(args.mode == 'pack2boca'):
        if(not args.all):
            pack2boca(args.problem_id)
        else:
            packall2boca()
