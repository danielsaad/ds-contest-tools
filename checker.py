#!/usr/bin/python3


# TODO: clean temporary files

import os
import subprocess
import sys
import time
import shutil
from metadata import Paths
from logger import info_log, debug_log, error_log
from time import sleep  # TODO - Delete before commit

""" Global definitions """

""" C definitions """
C_COMPILER = ['gcc']
C_FLAGS = ['-O2', '-DNDEBUG']
C_LFLAGS = ['-lm']

""" CPP definitions """
CPP_COMPILER = ['g++']
CPP_FLAGS = ['-O2', '-DNDEBUG', '-std=c++11']
CPP_LFLAGS = ['-lm']

""" Java definitions """
JAVA_COMPILER = ['javac']
JAVA_INTERPRETER = ['java']


""" Python3 definitions """
PYTHON3_INTERPRETER = ['python3']


def custom_key(str):
    return +len(str), str.lower()


def compile_c(submission_file, binary_file):
    """ Compile a source code 'submission_file' into its 
        corresponding 'binary_file' """
    command = C_COMPILER + C_FLAGS + \
        [submission_file] + ['-o', binary_file] + C_LFLAGS
    print('Compiling: ', ' '.join(command))
    p = subprocess.run(command)
    if (p.returncode):
        print('CE: C Compilation of', submission_file, 'Failed')
        sys.exit(1)
    else:
        print(binary_file, 'generated')


def compile_cpp(submission_file, binary_file):
    # submission_folder = os.path.basename(submission_file)
    command = CPP_COMPILER + CPP_FLAGS + \
        [submission_file] + ['-o', binary_file] + CPP_LFLAGS
    p = subprocess.run(command)
    print('Compiling: ', ' '.join(command))
    if (p.returncode):
        print('CE: C++ Compilation of', submission_file, 'Failed')
        sys.exit(1)
    else:
        print(binary_file, 'generated')


def compile_java(submission_file, problem_id):
    """ Compile a java file into problem_id.class """
    renamed_file = os.path.join(os.path.dirname(
        submission_file), problem_id) + '.java'
    shutil.copy2(submission_file, renamed_file)
    command = JAVA_COMPILER + [renamed_file]
    print('Compiling: ', ' '.join(command))
    p = subprocess.run(command)
    if (p.returncode):
        print('CE: Java Compilation of', renamed_file, 'Failed')
        sys.exit(1)
    else:
        print(renamed_file, 'class file', 'generated')


def run_binary(binary_file, input_folder, output_folder):
    test = os.path.basename(binary_file)
    debug_log('Run binary ' + test.upper())
    input_files = [f for f in os.listdir(
        input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_in = os.path.join(input_folder, fname_in)
        fname_out = os.path.join(output_folder, os.path.basename(fname_in))
        debug_log(f'Running test {os.path.basename(fname_in)}')
        local_time_start = time.perf_counter()
        with open(fname_in, 'r') as inf, open(fname_out, 'w') as ouf:
            p = subprocess.run([binary_file],
                               stdin=inf, stdout=ouf)
        local_time_end = time.perf_counter()
        if (p.returncode):
            debug_log('RE: Runtime error')
            # exit(0)
        debug_log('Time elapsed: {0:.2f}'.format(
            local_time_end-local_time_start) + ' seconds')


def run_java(class_name, input_folder, output_folder):
    input_files = [os.path.join(input_folder, f) for f in os.listdir(
        input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(class_name), 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir, os.path.basename(fname_in))
        print("Running test", os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in, 'r') as inf, open(fname_out, 'w') as ouf:
            command = JAVA_INTERPRETER + \
                ['-classpath',
                    os.path.dirname(class_name)] + [os.path.basename(class_name)]
            print(command)
            p = subprocess.run(command, stdin=inf, stdout=ouf)
        local_time_end = time.perf_counter()
        if (p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(
            local_time_end-local_time_start), 'seconds')


def run_python3(submission_file: str, input_folder: str, output_folder):
    input_files = [os.path.join(input_folder, f) for f in os.listdir(
        input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(submission_file), 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir, os.path.basename(fname_in))
        print("Running test", os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in, 'r') as inf, open(fname_out, 'w') as ouf:
            command = PYTHON3_INTERPRETER + [submission_file]
            p = subprocess.run(command, stdin=inf, stdout=ouf)
        local_time_end = time.perf_counter()
        if (p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(
            local_time_end-local_time_start), 'seconds')


def run(submission_file: str, input_folder: str, output_folder: str) -> None:
    binary_file, ext = os.path.splitext(submission_file)
    problem_folder = os.path.join(
        os.getcwd(), Paths.instance().dirs['problem_dir'])
    binary_file = os.path.join(problem_folder, 'bin', binary_file)
    start_time = 0.0
    end_time = 0.0
    if (ext == '.cpp'):
        start_time = time.perf_counter()
        run_binary(binary_file, input_folder, output_folder)
        end_time = time.perf_counter()
    elif (ext == '.c'):
        start_time = time.perf_counter()
        run_binary(binary_file, input_folder, output_folder)
        end_time = time.perf_counter()
    elif (ext == '.java'):
        problem_id = os.path.basename(os.path.dirname(input_folder))
        start_time = time.perf_counter()
        run_java(os.path.join(os.path.dirname(submission_file),
                 problem_id), input_folder, output_folder)
        end_time = time.perf_counter()
    elif (ext == '.py'):
        start_time = time.perf_counter()
        run_python3(submission_file, input_folder, output_folder)
        end_time = time.perf_counter()
    else:
        error_log(f'{submission_file} has an invalid extension')
        sys.exit(1)
    debug_log('Total time elapsed: {0:.2f}:'.format(end_time - start_time))


def run_checker(input_folder: str, output_folder: str, tmp_dir: str, checker_file: str) -> None:
    output_files = [os.path.join(output_folder, f) for f in os.listdir(
        output_folder) if os.path.isfile(os.path.join(output_folder, f))]
    output_files.sort(key=custom_key)
    error_found = False
    for f in output_files:
        fname = os.path.basename(f)
        inf = os.path.join(input_folder, fname)
        ouf = f
        ans = os.path.join(tmp_dir, fname)
        if (not os.path.isfile(inf)):
            error_log('Input' + fname + 'not available')
            sys.exit(1)
        if (not os.path.isfile(ans)):
            error_log('Answer' + fname + 'not available')
            sys.exit(1)
        debug_log('Checking input ' + fname)
        command = [checker_file, inf, ouf, ans]
        p = subprocess.run(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        checker_output = p.stderr.decode('utf-8')
        if (checker_output.startswith('ok')):
            debug_log('Input ' + fname + ': AC')
        elif (checker_output.startswith('wrong answer')):
            debug_log('Input ' + fname + ': WA')
            error_found = True
        elif (checker_output.startswith('wrong output format')):
            debug_log('Input ' + fname + ': PE')
            error_found = True
        elif (checker_output.startswith('FAIL Unexpected')):
            debug_log(f'Input {fname}: RE')
            error_found = True
            # TODO : Esclarecer essa saída com o Saad
        elif (checker_output.startswith('FAIL')):
            error_log('Input ' + fname +
                      ': FAIL: maybe the jury solution or the checker are not correct')
            error_found = True
        else:
            error_log(
                f'Input {fname}: Output not recognized -> {checker_output}')
            error_found = True
    if not error_found:
        info_log('OK: All tests passed!')


# TODO - write documentation


def run_solutions(input_folder, output_folder, problem_metadata) -> None:
    solutions = problem_metadata['solutions']
    problem_folder = Paths.instance().dirs["problem_dir"]
    tmp_folder = os.path.join(os.getcwd(), problem_folder, 'tmp_output')
    os.makedirs(tmp_folder, exist_ok=True)

    for expected_result, files in solutions.items():
        if isinstance(files, list):
            for submission_file in files:
                if submission_file != '':
                    info_log(f'Running {submission_file.upper()} solution')
                    run(submission_file, input_folder, tmp_folder)
                    run_checker(input_folder, output_folder,
                                tmp_folder, os.path.join(problem_folder, 'bin/checker'))
        else:
            info_log(f'Running {files.upper()} solution')
            run(files, input_folder, tmp_folder)
            run_checker(input_folder, output_folder,
                        tmp_folder, os.path.join(problem_folder, 'bin/checker'))
    shutil.rmtree(tmp_folder)
