#!/usr/bin/python3

import os
import queue
import subprocess
import sys
import time
from multiprocessing import Event, Manager, Pipe, Process, Queue
from multiprocessing.connection import Connection
from multiprocessing.managers import DictProxy
from signal import SIGKILL

import psutil

from logger import debug_log, error_log, info_log
from metadata import Paths, Problem, ProblemAnswer, Solution, Status, Test

""" Java definitions """
JAVA_INTERPRETER = 'java'
JAVA_FLAG = '-classpath'

""" Python3 definitions """
PYTHON3_INTERPRETER = 'python3'


def custom_key(string_to_sort: str) -> tuple:
    """
    Custom key to sort strings based on length and lowercase alphabetical order.

    Args:
        string_to_sort: The string to sort.

    Returns:
        tuple: A tuple containing the length of the string and its lowercase version.

    """
    return +len(string_to_sort), string_to_sort.lower()


def run_binary(problem_obj: Problem, solution: Solution, input_files: list, output_dict, pids: Queue,
               pace: int, begin: int) -> None:
    """
    Runs the compiled binary for a given solution and populates the output dictionary.

    Args:
        problem_obj: The problem object.
        solution: The solution object containing the executable.
        input_files: The list of input files.
        output_dict (Dict[int, Test]): The dictionary to populate with the test results.
        pids: The queue to add PIDs to.
        pace: The number of input files to process at a time.
        begin: The index of the first file to process.

    """
    ans_folder = os.path.join(problem_obj.problem_dir, 'output')

    conn_sender, con_recv = Pipe()
    for i in range(begin, len(input_files), pace):
        ans_file: str = os.path.join(ans_folder, input_files[i])
        fname_in: str = os.path.join(problem_obj.input_folder, input_files[i])
        fname_out: str = os.path.join(solution.output_path, input_files[i])

        status: Status = Status.AC
        checker_output: str = None
        memory_info: tuple = (0, 0)
        with open(fname_in, 'r') as inf, open(fname_out, 'w') as ouf:
            local_time_start = time.perf_counter()
            local_time_end = 0
            total_time_elapsed = 0
            p = subprocess.Popen(solution.exec_args,
                                 stdin=inf, stdout=ouf, stderr=subprocess.PIPE, text=True)
            pids.put([p.pid, conn_sender])
            try:
                _, stderr = p.communicate(
                    timeout=2 * problem_obj.time_limit)
                if p.returncode < 0 or stderr:
                    status = Status.RE
            except subprocess.TimeoutExpired:
                status = Status.HARD_TLE
                p.kill()
                _, stderr = p.communicate()
            finally:
                local_time_end = time.perf_counter()
                total_time_elapsed = local_time_end - local_time_start
                memory_info = con_recv.recv()
            if memory_info[1] != Status.AC:
                status = Status.MLE
                if total_time_elapsed > problem_obj.time_limit:
                    status = Status.TLE_MLE
            elif status == Status.AC:
                status, checker_output = run_checker(
                    ans_file, fname_in, fname_out)
                if total_time_elapsed > problem_obj.time_limit and status == Status.AC:
                    status = Status.SOFT_TLE

            test_info: Test = Test(i, total_time_elapsed,
                                   memory_info[0], status, checker_output)
            output_dict[i] = test_info
    con_recv.close()
    conn_sender.close()


def run(problem_obj: Problem, solution: Solution, cpu_number: int) -> None:
    """
    Runs a solution to a given problem using multiple threads.

    Args:
        problem_obj: The problem to solve.
        solution: The solution to the problem.
        cpu_number: The number of CPU cores to use.

    """
    output_folder: str = solution.output_path
    os.makedirs(output_folder, exist_ok=True)
    debug_log(f'Run solution {solution.solution_name}')

    solution.exec_args = identify_language(problem_obj, solution)
    start_time: float = time.perf_counter()
    create_processes(problem_obj, solution, cpu_number)
    end_time: float = time.perf_counter()
    debug_log(f'Total time elapsed: {end_time - start_time:.2f}\n')


def identify_language(problem_obj: Problem, solution: Solution) -> str:
    """
    Identifies the programming language of the solution and returns the appropriate command-line arguments.

    Args:
        problem_obj: The problem being solved.
        solution: The solution to the problem.

    Returns:
        str: The command-line arguments needed to execute the solution.
    """
    binary_file: str = solution.get_binary_name()
    ext: str = solution.get_file_extension()
    problem_folder = problem_obj.problem_dir
    exec_args: str

    if (ext == 'cpp' or ext == 'c'):
        exec_args = os.path.join(problem_folder, 'bin', binary_file)
    elif (ext == 'java'):
        problem_id = os.path.join(problem_folder, 'bin')
        exec_args = f'{JAVA_INTERPRETER} {JAVA_FLAG} {problem_id} {solution.get_binary_name()}'
    elif (ext == 'py'):
        submission_file = os.path.join(
            problem_folder, 'src', solution.solution_name)
        exec_args = f'{PYTHON3_INTERPRETER} {submission_file}'
    else:
        error_log(f'{solution.solution_name} has an invalid extension')
        sys.exit(1)

    return exec_args


def run_checker(ans: str, inf: str, ouf: str) -> tuple:
    """
    Runs the checker binary file and returns the status and checker output.

    Args:
        ans: The path to the answer file.
        inf: The path to the input file.
        ouf: The path to the output file.

    Returns:
        A tuple containing the status (one of Status.AC, Status.WA, Status.PE, or Status.FAIL) 
        and the output of the checker as a string.
    """
    fname = os.path.basename(inf)
    status = Status.AC
    checker_file: str = os.path.join(
        Paths().get_problem_dir(), 'bin/checker')
    if (not os.path.isfile(inf)):
        error_log('Input ' + fname + ' not available')
        sys.exit(1)
    if (not os.path.isfile(ans)):
        error_log('Answer ' + fname + ' not available')
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
        status = Status.FAIL
    else:
        status = Status.PE
    return status, checker_output


def run_solutions(problem_obj: Problem, cpu_number: int) -> None:
    """
    Runs all the solutions in the given problem using the specified number of CPUs.

    Args:
        problem_obj: The problem object containing the solutions to run.
        cpu_number: The number of CPUs to use.

    """
    solutions = problem_obj.get_list_solution()
    for i in solutions:
        solution: Solution = i
        running: str = f'Running {solution.solution_name}'
        info_log(running)
        run(problem_obj, solution, cpu_number)
        solution_status(solution)


def create_processes(problem_obj: Problem, solution: Solution, cpu_number: int) -> None:
    """
    Creates and starts multiple processes to run a given solution with multiple input files.

    Args:
        problem_obj: A Problem object representing the problem being solved.
        solution: A Solution object representing the solution being tested.
        cpu_number: An integer representing the maximun number of CPUs to use for running the solution.

    """
    n_threads = process_cpu_number(solution.expected_result, cpu_number)
    input_files = [f for f in os.listdir(
        problem_obj.input_folder) if os.path.isfile(os.path.join(problem_obj.input_folder, f))]
    input_files.sort(key=custom_key)
    with Manager() as manager:
        pids: Queue = Queue(maxsize=100)
        stop_monitor: Event = manager.Event()
        output_dict: DictProxy = manager.dict()
        monitor_process = Process(target=memory_monitor, args=(
            pids, problem_obj.memory_limit, stop_monitor))
        monitor_process.start()

        processes = [Process(target=run_binary, args=(problem_obj, solution, input_files,
                             output_dict, pids, n_threads, idx)) for idx in range(n_threads)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        stop_monitor.set()
        processes = Process(target=write_to_log, args=(output_dict,))
        processes.start()
        monitor_process.join()
        solution.add_tests(dict(output_dict))
        processes.join()


def write_to_log(output_dict: DictProxy) -> None:
    """
    Write test results to the debug log.

    Args:
        output_dict: Shared dictionary containing the test results.
    """
    for i in range(len(output_dict)):
        debug_log(f'Running test {i + 1}')
        if output_dict[i].status == Status.AC:
            debug_log('AC: Accepted')
        elif output_dict[i].status == Status.WA:
            debug_log('WA: Wrong answer')
        elif output_dict[i].status == Status.RE:
            debug_log('RE: Runtime error')
        elif output_dict[i].status == Status.HARD_TLE or output_dict[i].status == Status.SOFT_TLE:
            debug_log('TLE: Time limit exceeded')
        elif output_dict[i].status == Status.MLE:
            debug_log('ML: Memory limit exceeded')
        elif output_dict[i].status == Status.PE:
            debug_log('PE: Presentation Error')

        debug_log(f'Time elapsed: {output_dict[i].exec_time:.2f} seconds')
        debug_log(f'Memory: {output_dict[i].memory_usage // 1000} KB')


def solution_status(solution: Solution) -> None:
    """
    Sets the solution status based on the status of its tests.

    Args:
        solution: The solution object to be evaluated.

    """
    test_cases_status: dict = dict()
    solution_result: ProblemAnswer = ProblemAnswer.WRONG

    for _, test in solution.tests.items():
        test_cases_status[test.status] = test_cases_status.get(
            test.status, 0) + 1

    expected_status = {
        "ACCEPTED": [Status.AC],
        'WRONG ANSWER': [Status.WA],
        'TIME LIMIT EXCEEDED': [Status.HARD_TLE, Status.SOFT_TLE],
        'RUNTIME ERROR': [Status.RE],
        'MEMORY LIMIT EXCEEDED': [Status.MLE],
        'PRESENTATION ERROR': [Status.PE]
    }

    for result_status, _ in test_cases_status.items():
        if result_status in expected_status[solution.expected_result]:
            solution_result = ProblemAnswer.CORRECT
        elif result_status not in expected_status[solution.expected_result] and result_status != Status.AC:
            solution_result = ProblemAnswer.WRONG
            break
    solution.solution_status = solution_result


def memory_monitor(pids: Queue, memory_limit: int, stop_monitor: Event) -> None:
    """
    Monitors the memory usage of running processes and kills them if their memory usage exceeds the given memory limit.

    Args:
        pids: A queue of tuples containing process ID and a connection object to communicate with the process.
        memory_limit: The maximum memory limit allowed for each process.
        stop_monitor: An event object to signal the monitor to stop.

    """
    mem_usage: dict = dict()
    status: dict = dict()
    while not stop_monitor.is_set():
        try:
            process = pids.get(timeout=0.5)
            process_pid: int = process[0]
            mem_usage[process_pid] = mem_usage.get(process_pid, 0)
            conn: Connection = process[1]
            process_info = psutil.Process(process_pid)
            mem_usage[process_pid] = (
                max(process_info.memory_info().rss, mem_usage[process_pid]))
            if (mem_usage[process_pid] > memory_limit):
                status[process_pid] = status.get(process_pid, Status.MLE)
                try:
                    os.kill(process_pid, SIGKILL)
                except:
                    pass
            pids.put(process)
        except queue.Empty:
            pass
        except psutil.NoSuchProcess:
            conn.send((mem_usage[process_pid],
                       status.get(process_pid, Status.AC)))


def process_cpu_number(expected_result: str, cpu_number: int) -> int:
    return 1 if expected_result == 'main-ac' else cpu_number
