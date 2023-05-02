import hashlib
import os
import shutil
import subprocess
import sys
from typing import Dict
from metadata import Problem, Solution

from checker import run_solutions
from config import custom_key
from htmlutils import print_to_html
from jsonutils import parse_json
from logger import debug_log, error_log, info_log
from metadata import Paths
from utils import (check_problem_metadata, check_subprocess_output,
                   generate_timestamp, verify_path)


def build_executables() -> None:
    """Run Makefile to create release and debug executables."""
    old_cwd = os.getcwd()
    os.chdir(Paths().get_problem_dir())

    # Verify necessary files
    verify_path(os.path.join('src', 'testlib.h'))
    verify_path(os.path.join('src', 'checker.cpp'))

    info_log("Compiling executables")
    p = subprocess.run(['make', '-j'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    check_subprocess_output(p, "Makefile failed.")
    os.chdir(old_cwd)


def run_programs(all_solutions: bool = False, specific_solution: str = '', cpu_number: int = 0) -> None:
    """
    Run the executables to create the problem.

    Args:
        all_solutions: Boolean indicating whether to run all solution files.
        specific_solution: String containing name of the solution to run.
    """
    problem_folder = Paths().get_problem_dir()
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    problem_obj = Problem(problem_metadata["problem"]["title"],
                          problem_folder, input_folder, problem_metadata["problem"]["time_limit"], problem_metadata["problem"]["memory_limit_mb"])
    parse_solutions(
        problem_obj, problem_metadata['solutions'], all_solutions, specific_solution)
    generate_inputs()
    validate_inputs()
    produce_outputs(problem_metadata)

    info_log("Running solutions")
    run_solutions(problem_obj, cpu_number)
    print_to_html(problem_obj)


def get_encoded_tests(input_folder: str) -> Dict[str, bytes]:
    """
    Get a dictionary of encoded test files from a input folder.

    Args:
        tests_folder: Path to the tests folder.

    Returns:
        A dictionary which contains the encoded version of the input files in bytes.
    """
    files: list = [f for f in os.listdir(
        input_folder) if not f.endswith('.interactive')]
    files.sort(key=custom_key)
    files_path: list = [os.path.join(input_folder, f) for f in files]
    return encode_tests(files_path)


def encode_tests(input_files: list) -> Dict[str, bytes]:
    """
    Generates a dictionary of SHA-1 hash values of input file.

    Args:
        input_files: List containing paths to input files.

    Returns:
        A dictionary which contains the encoded version of the input files in bytes.
    """
    tests = dict()
    for fname in input_files:
        with open(fname, 'rb') as f:
            encoded = (hashlib.sha1(f.read())).digest()
            tests.setdefault(encoded, []).append(fname)
    return tests


def validate_inputs() -> None:
    """Validate input files by running the validator file."""
    problem_dir = Paths().get_problem_dir()
    validator_path = os.path.join(problem_dir, 'bin', 'validator')
    input_folder = os.path.join(problem_dir, 'input')
    verify_path(validator_path)

    # Check each input file with the validator
    input_files = [f for f in os.listdir(input_folder) if os.path.isfile(f)
                   and not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    for fname in input_files:
        with open(os.path.join(input_folder, fname)) as f:
            p = subprocess.Popen([validator_path],
                                 stdin=f, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            out, err = p.communicate()
            if out or err:
                error_log(out)
                error_log(err)
                error_log("Failed validation on input", fname)
                sys.exit(1)

    # Check for equal test cases
    equal_tests = 0
    encoded_tests = encode_tests(input_files)
    for key in encoded_tests:
        if len(encoded_tests[key]) > 1:
            equal_tests += len(encoded_tests[key])
            debug_log("Testcases " +
                      ', '.join(encoded_tests[key]) + " are equal.")
    if equal_tests:
        error_log("All test cases must be different, however there are " +
                  f"{equal_tests} equal tests.")
        sys.exit(0)


def get_manual_tests(temporary_folder: str) -> list:
    """Get manual tests generated without the source generators.

    Args:
        temporary_folder: Path to the temporary input folder.

    Returns:
        A list containing the absolute path of manual tests of the problem.
    """
    problem_dir = Paths().get_problem_dir()

    temporary_encoded_tests: dict = get_encoded_tests(temporary_folder)
    original_encoded_tests: dict = get_encoded_tests(
        os.path.join(problem_dir, 'input'))

    manual_tests = set()
    for key, value in original_encoded_tests.items():
        if key in temporary_encoded_tests:
            continue

        for test in value:
            manual_tests.add(test)

    return list(manual_tests)


def move_inputs(temporary_folder: str) -> None:
    """Move input files from temporary folder to problem folder, ignoring
    repeated testcases.

    Args:
        temporary_folder: Path to the temporary folder.
    """
    info_log("Moving input tests to problem folder.")
    problem_dir = Paths().get_problem_dir()
    input_folder: str = os.path.join(problem_dir, 'input')

    temporary_encoded_files: dict = get_encoded_tests(temporary_folder)
    original_encoded_tests: dict = get_encoded_tests(input_folder)

    repeated_tests = set()
    for key, values in temporary_encoded_files.items():
        if key in original_encoded_tests:
            for value in values:
                repeated_tests.add(os.path.basename(value))

    index = 1
    output_folder = os.listdir(temporary_folder)
    output_folder.sort(key=custom_key)
    for input_test in output_folder:
        if input_test in repeated_tests:
            continue
        while os.path.exists(os.path.join(input_folder, str(index))):
            index += 1
        shutil.move(os.path.join(temporary_folder, str(input_test)),
                    os.path.join(input_folder, str(index)))


def generate_script_inputs(generator_path: str, script: list, output_path: str) -> None:
    """Generate input files from script.

    Args:
        generator_path: Path to the generator used in the script.
        script: Script line containing commands for generator.
        output_path: Path to store the input files.
    """
    script[0] = generator_path
    p: subprocess.CompletedProcess = subprocess.run(
        [*script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    script_result: str = p.stdout
    p.stdout = ""
    check_subprocess_output(p, "Error generating inputs.")

    with open(output_path, 'w') as input_file:
        input_file.write(script_result)


def generate_inputs(move: bool = True, output_folder: str = '') -> None:
    """Generates input files inside temporary directory.

    Args:
        move: If the input files will be moved to the problem folder. Defaults to True.
    """
    problem_dir = Paths().get_problem_dir()
    script_path: str = os.path.join(problem_dir, 'src', 'script.sh')
    generator_path: str = os.path.join(problem_dir, 'bin', 'generator')

    if output_folder == '':
        output_folder = os.path.join(
            '/', 'tmp', f'ds-contest-tool-{generate_timestamp()}', 'input')
    os.makedirs(output_folder, exist_ok=True)

    scripts: list = []
    ds_generator: bool = True

    # Verify existence of at least one generator
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            scripts: list = f.readlines()

        for script in scripts:
            if script.startswith('generator '):
                ds_generator = False
                break
    elif not os.path.exists(generator_path):
        error_log("No generators or scripts found.")
        sys.exit(1)

    # Verify and run a DS generator
    if ds_generator and os.path.exists(generator_path):
        info_log("Generating inputs of DS generator")
        old_cwd = os.getcwd()
        os.chdir(output_folder)
        p: subprocess.CompletedProcess = subprocess.run(
            generator_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        check_subprocess_output(p, "Error generating inputs.")
        os.chdir(old_cwd)

    # Generate tests from script
    index: int = len(os.listdir(output_folder)) + 1
    for script in scripts:
        debug_log(f"Generating script '{script.rstrip()}'.")
        script = script.split()
        generator_path = os.path.join(problem_dir, 'bin', script[0])
        verify_path(generator_path)

        generate_script_inputs(generator_path, script,
                               os.path.join(output_folder, str(index)))
        index += 1

    move_inputs(output_folder) if move else None


def produce_outputs(problem_metadata: dict) -> None:
    """
    Run main solution on inputs to produce the outputs.

    Args:
        problem_metadata (dict): Dictionary containing the values of problem.json.
    """
    info_log("Producing outputs")
    problem_dir = Paths().get_problem_dir()
    input_folder = os.path.join(problem_dir, 'input')
    output_folder = os.path.join(problem_dir, 'output')
    input_files: list = [f for f in os.listdir(input_folder)
                         if not f.endswith('.interactive')]
    for fname in input_files:
        inf_path: str = os.path.join(input_folder, fname)
        ouf_path: str = os.path.join(output_folder, fname)
        with open(inf_path, 'r') as inf, open(ouf_path, 'w') as ouf:
            ac_solution: str = os.path.join(
                problem_dir, 'bin', os.path.splitext(problem_metadata["solutions"]["main-ac"])[0])
            if problem_metadata["problem"]["interactive"]:
                interactor: str = os.path.join(
                    problem_dir, 'bin', 'interactor')
                verify_path(interactor)
                tmp_fifo = os.path.join(output_folder, 'tmpfifo')
                if os.path.exists(tmp_fifo):
                    info_log("Removing existing FIFO")
                    subprocess.run(['rm', tmp_fifo])
                subprocess.run(['mkfifo', tmp_fifo])

                command: list = [interactor, inf_path, ouf_path, '<',
                                 tmp_fifo, '|', ac_solution, '>', tmp_fifo]

                p: subprocess.CompletedProcess = subprocess.run(
                    ' '.join(command), stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, shell=True)
                subprocess.run(['rm', tmp_fifo])
            else:
                p: subprocess.CompletedProcess = subprocess.run(
                    [ac_solution], stdin=inf, stdout=ouf, stderr=subprocess.PIPE,
                    text=True, encoding='utf-8')
            check_subprocess_output(
                p, f"Generation of output failed for input {fname}")
    info_log("Outputs produced successfully.")


def clean_files() -> None:
    """Call Makefile in order to remove executables."""
    old_cwd: str = os.getcwd()
    os.chdir(Paths().get_problem_dir())
    verify_path('Makefile')

    command: list = ['make', 'clean']
    p: subprocess.CompletedProcess = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    check_subprocess_output(p, "Error cleaning executables.")
    os.chdir(old_cwd)


def parse_solutions(problem_obj: Problem, solutions: dict, all_solutions, specific_solution: str) -> None:
    solution: Solution = None
    if all_solutions:
        for expected_result, files in solutions.items():
            if len(files) == 0:
                continue
            if isinstance(files, list):
                for submission_file in files:
                    solution = Solution(submission_file, expected_result)
                    problem_obj.add_solution(solution)
            else:
                submission_file = files
                solution = Solution(submission_file, expected_result)
                problem_obj.add_solution(solution)
    else:
        if specific_solution:
            for expected_result, files in solutions.items():
                if len(files) == 0:
                    continue
                if isinstance(files, list):
                    for submission_file in files:
                        if submission_file == specific_solution:
                            solution = Solution(
                                submission_file, expected_result)
                            problem_obj.add_solution(solution)
                else:
                    submission_file = files
                    if submission_file == specific_solution:
                        solution = Solution(submission_file, expected_result)
                        problem_obj.add_solution(solution)

            if problem_obj.is_solution_list_empty():
                error_log(f'Solution {specific_solution} not found.')
                sys.exit(0)
        else:
            expected_result = "main-ac"
            submission_file = solutions[expected_result]
            solution = Solution(submission_file, expected_result)
            problem_obj.add_solution(solution)

    return
