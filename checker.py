#!/usr/bin/python3


# TODO: clean temporary files

import os
from signal import SIGKILL
import subprocess
import sys
import time
import shutil
import psutil
from enum import Enum
from multiprocessing import Process, cpu_count, Manager, Event, Pipe, Pool
from metadata import Paths
from logger import info_log, debug_log, error_log


class Status(Enum):
    AC = 0
    WA = 1
    RE = 2
    MLE = 3
    TLE = 4
    PE = 5
    AC_TLE = 6
    TLE_MLE = 7


""" Java definitions """
JAVA_COMPILER = ['javac']
JAVA_INTERPRETER = ['java']


""" Python3 definitions """
PYTHON3_INTERPRETER = ['python3']


def custom_key(str):
    return +len(str), str.lower()


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


def run_binary(binary_file: str, input_folder: str, output_folder: str,
               input_files: list, output_dict, problem_limits: dict,
               begin: int = 0, pace: int = 1):
    ans_folder = os.path.join(
        Paths.instance().dirs["problem_dir"], 'output')
    for i in range(begin, len(input_files), pace):
        ans_file = os.path.join(ans_folder, input_files[i])
        fname_in = os.path.join(input_folder, input_files[i])
        fname_out = os.path.join(output_folder, input_files[i])
        status = Status.AC
        event = Event()
        conn_sender, con_recv = Pipe()
        mem_info = (0, 0)
        with open(fname_in, 'r') as inf, open(fname_out, 'w') as ouf:
            local_time_start = time.perf_counter()
            local_time_end = 0
            total_time_elapsed = 0
            try:
                p = subprocess.Popen([binary_file],
                                     stdin=inf, stdout=ouf, stderr=subprocess.PIPE)
                process = Process(target=memory_monitor,
                                  args=(p.pid, problem_limits['memory_limit'], event, conn_sender))
                process.start()
                p.communicate(timeout=2*problem_limits['time_limit'])
                if p.returncode < 0:
                    status = Status.RE
            except subprocess.TimeoutExpired:
                status = Status.TLE
            finally:
                local_time_end = time.perf_counter()
                total_time_elapsed = local_time_end - local_time_start
                event.set()
                mem_info = con_recv.recv()
            if mem_info[1] != Status.AC:
                status = Status.MLE
                if total_time_elapsed > problem_limits['time_limit']:
                    status = Status.TLE_MLE
            elif status == Status.AC:
                status = run_checker(ans_file, fname_in, fname_out)
                if total_time_elapsed > problem_limits['time_limit'] and status == Status.AC:
                    status = Status.AC_TLE
            output_dict[i] = [status, total_time_elapsed, mem_info[0]]


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


def run(submission_file: str, input_folder: str, output_folder: str,
        problem_limits: dict, expected_result: str) -> None:
    binary_file, ext = os.path.splitext(submission_file)
    debug_log('Run binary ' + binary_file)
    problem_folder = os.path.join(
        os.getcwd(), Paths.instance().dirs['problem_dir'])
    binary_file = os.path.join(problem_folder, 'bin', binary_file)
    start_time = 0.0
    end_time = 0.0
    input_files = [f for f in os.listdir(
        input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    input_files.sort(key=custom_key)
    if (ext == '.cpp' or ext == '.c'):
        start_time = time.perf_counter()
        create_thread(binary_file, input_folder,
                      output_folder, input_files, run_binary, problem_limits, expected_result)
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


def run_checker(ans: str, inf: str, ouf: str) -> Status:
    fname = os.path.basename(inf)
    status = Status.AC
    checker_file: str = os.path.join(
        Paths.instance().dirs["problem_dir"], 'bin/checker')
    if (not os.path.isfile(inf)):
        error_log('Input' + fname + 'not available')
        sys.exit(1)
    if (not os.path.isfile(ans)):
        error_log('Answer' + fname + 'not available')
        sys.exit(1)
    command = [checker_file, inf, ouf, ans]
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    checker_output = p.stderr.decode('utf-8')
    if (checker_output.startswith('ok')):
        status = Status.AC
    elif (checker_output.startswith('wrong answer')):
        status = Status.WA
    elif (checker_output.startswith('FAIL')):
        error_log('Input ' + fname +
                  ': FAIL: maybe the jury solution or the checker are not correct')
    else:
        status = Status.PE
    return status

# TODO - write documentation


def run_solutions(input_folder, problem_metadata, all_solutions: bool) -> None:
    time_limit = problem_metadata["problem"]["time_limit"]
    memory_limit = problem_metadata["problem"]["memory_limit_mb"] * 2 ** 20
    problem_limits = {'time_limit': time_limit,
                      'memory_limit': memory_limit}
    solutions = problem_metadata['solutions']
    problem_folder = Paths.instance().dirs["problem_dir"]
    tmp_folder = os.path.join(os.getcwd(), problem_folder, 'tmp_output')
    os.makedirs(tmp_folder, exist_ok=True)
    if all_solutions:
        for expected_result, files in solutions.items():
            if isinstance(files, list):
                for submission_file in files:
                    if submission_file != '':
                        info_log(f'Running {submission_file} solution')
                        run(submission_file, input_folder,
                            tmp_folder, problem_limits, expected_result)
            else:
                info_log(f'Running {files} solution')
                run(files, input_folder, tmp_folder,
                    problem_limits, expected_result)
    else:
        expected_result = "main-ac"
        submission_file = solutions[expected_result]
        info_log(f'Running {submission_file} solution')
        run(submission_file, input_folder, tmp_folder,
            problem_limits, expected_result)
    shutil.rmtree(tmp_folder)


def create_thread(binary_file, input_folder, output_folder, input_files: list, routine, problem_limits: dict, expected_result: str):
    solution_tp = True if expected_result == "main-ac" or expected_result == "alternative-ac" else False
    n_threads = 1 if solution_tp else max(cpu_count()//2, 1)

    with Manager() as manager:
        output_dict = manager.dict()
        processes = [Process(target=routine, args=(
            binary_file, input_folder, output_folder, input_files, output_dict, problem_limits, idx, n_threads)) for idx in range(n_threads)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        write_to_log(output_dict)


def write_to_log(output_dict):
    for i in range(len(output_dict)):
        debug_log(f'Running test {i + 1}')
        if output_dict[i][0] == Status.AC:
            debug_log('AC: Accepted')
        elif output_dict[i][0] == Status.WA:
            debug_log('WA: Wrong answer')
        elif output_dict[i][0] == Status.RE:
            debug_log('RE: Runtime error')
        elif output_dict[i][0] == Status.TLE:
            debug_log('TLE: Time limit exceeded')
        elif output_dict[i][0] == Status.MLE:
            debug_log('ML: Memory limit exceeded')
        elif output_dict[i][0] == Status.PE:
            debug_log('PE: Presentation Error')
        elif output_dict[i][0] == Status.AC_TLE:
            debug_log('AC or TLE: Accepted or Time limit exceeded')
        elif output_dict[i][0] == Status.TLE_MLE:
            debug_log(
                'TLE or MLE: d or Time limit exceeded or Memory limit exceeded')
        debug_log('Time elapsed: {0:.2f}'.format(
            output_dict[i][1]) + ' seconds')
        debug_log(f'Memory: {output_dict[i][2]/1000} KB')


def memory_monitor(pid: int, memory_limit: int, event, con) -> None:
    mem_usage = 0
    status = Status.AC
    try:
        while (not event.is_set()):
            process = psutil.Process(pid)
            mem_usage = (max(process.memory_info().rss, mem_usage))
            if (mem_usage > memory_limit):
                status = Status.MLE
                os.kill(pid, SIGKILL)
                return
            time.sleep(0.05)
    except psutil.NoSuchProcess:
        return
    finally:
        con.send((mem_usage, status))
