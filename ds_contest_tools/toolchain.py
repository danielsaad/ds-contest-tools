import hashlib
import os
import shutil
import subprocess
from typing import Dict

from .checker import run_solutions
from .config import IGNORED_DIRS, custom_key
from .htmlutils import print_to_html
from .jsonutils import parse_json, write_to_json
from .logger import debug_log, error_log, info_log, warning_log
from .metadata import Paths, Problem, Solution
from .utils import check_problem_metadata, check_subprocess_output, verify_path, copy_files

""" Java definitions """
JAVA_INTERPRETER = 'java'
JAVA_FLAG = '-classpath'

""" Python3 definitions """
PYTHON3_INTERPRETER = 'python3'


def init_problem(interactive: bool, grader: bool, verify_folder: bool = True, ignore_patterns: list = IGNORED_DIRS) -> None:
    """Initialize a problem.

    Args:
        interactive: Boolean indicating whether the problem is interactive.
        grader: Boolean indicating whether the problem is a grader.
    """
    problem_folder = Paths().get_problem_dir()
    src_folder = os.path.join(problem_folder, 'src')
    json_path = os.path.join(problem_folder, 'problem.json')
    if verify_folder and os.path.exists(src_folder):
        error_log("Problem ID already exists in the directory")

    # Copy standard files to problem folder
    tool_folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'files')
    shutil.copytree(tool_folder, problem_folder,
                    ignore=shutil.ignore_patterns(*ignore_patterns), dirs_exist_ok=True)
    remove_src_files = ['sqtpm.sh']
    for file in remove_src_files:
        os.remove(os.path.join(problem_folder, file))

    # Verify grader problem
    problem_json = parse_json(json_path)
    if grader:
        problem_json['problem']['grader'] = True
        write_to_json(json_path, problem_json)
    elif verify_folder:
        os.remove(os.path.join(src_folder, 'grader.cpp'))
        os.remove(os.path.join(src_folder, 'grader.h'))

    # Verify interactive problem
    if interactive:
        # Create .interactive files for statement
        os.makedirs(os.path.join(problem_folder, 'input'))
        os.makedirs(os.path.join(problem_folder, 'output'))
        open(os.path.join(
            *[problem_folder, 'input', '1.interactive']), 'w').close()
        open(os.path.join(
            *[problem_folder, 'output', '1.interactive']), 'w').close()
        # Update problem.json to indicate that the problem is interactive
        problem_json['problem']['interactive'] = True
        write_to_json(json_path, problem_json)
    elif verify_folder:
        interactor = os.path.join(src_folder, 'interactor.cpp')
        interactor_tex = os.path.join(
            problem_folder, 'statement', 'interactor.tex')
        os.remove(interactor_tex)
        os.remove(interactor)


def prepare_grader_problem(grader_folder: str, handler_folder: str, problem_json: dict) -> None:
    """Create temporary folders to compile grader problem.

    Args:
        grader_folder: Path to the grader folder.
        handler_folder: Path to the handler folder.
        problem_json: Dictionary containing the values of problem.json.
    """
    src_dir = 'src'
    grader_files = set()
    grader_files.add('grader.cpp')

    # Copy grader libs to grader folder
    all_files = set([f for f in os.listdir(src_dir)
                    if not os.path.isdir(os.path.join(src_dir, f))])
    grader_libs = [f for f in all_files if f.endswith(
        '.h') and f != 'testlib.h']
    copy_files(src_dir, grader_folder, grader_libs)
    grader_files.update(grader_libs)

    # Copy solutions to grader folder
    for solution in problem_json['solutions'].values():
        if isinstance(solution, str):
            solution = [solution]
        solution = [f for f in solution if f.endswith('.cpp')]
        copy_files(src_dir, grader_folder, solution)
        grader_files.update(solution)

    # Copy other files to handler folder
    other_files = all_files - grader_files
    copy_files(src_dir, handler_folder, other_files)


def build_executables(no_checker: bool = False) -> None:
    """Run Makefile to create release and debug executables."""
    old_cwd = os.getcwd()
    os.chdir(Paths().get_problem_dir())

    # Verify necessary files
    verify_path('Makefile')
    verify_path('problem.json')
    verify_path(os.path.join('src', 'testlib.h'))
    if not no_checker:
        verify_path(os.path.join('src', 'checker.cpp'))

    # Verify grader problem
    problem_json = parse_json('problem.json')
    check_problem_metadata(problem_json)
    grader_problem = problem_json['problem']['grader']
    grader_folder = os.path.join('src', 'grader')
    handler_folder = os.path.join('src', 'handler')
    if grader_problem:
        prepare_grader_problem(grader_folder, handler_folder, problem_json)

    info_log("Compiling executables")
    command = ['make', '-j']
    p = subprocess.run(command,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check_subprocess_output(p, "Makefile failed.")

    if grader_problem:
        shutil.rmtree(grader_folder)
        shutil.rmtree(handler_folder)

    os.chdir(old_cwd)


def run_programs(all_solutions: bool = False, specific_solution: str = '', cpu_number: int = 1, no_validator: bool = False, no_generator: bool = False, no_checker: bool = False, no_output: bool = False) -> None:
    """
    Run the executables to create the problem.

    Args:
        all_solutions: Boolean indicating whether to run all solution files.
        specific_solution: String containing name of the solution to run.
        cpu_number: Number of CPUs to use.
        no_validator: Boolean indicating whether to run the validator or not.
        no_generator: Boolean indicating whether to run the generator or not.
        no_checker: Boolean indicating whether to run the checker or not.
        no_output: Boolean indicating whether to generate output files or not.
    """
    problem_folder = Paths().get_problem_dir()
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    problem_obj = Problem(problem_metadata["problem"]["title"],
                          problem_folder, input_folder,
                          problem_metadata["problem"]["time_limit"],
                          problem_metadata["problem"]["memory_limit_mb"])

    grader: bool = problem_metadata['problem']['grader']
    parse_solutions(
        problem_obj, problem_metadata['solutions'], all_solutions, specific_solution, grader)

    if not no_generator:
        generate_inputs()
    if not no_validator:
        validate_inputs()
    if not no_output:
        produce_outputs(problem_obj, problem_metadata)
    if not no_checker:
        info_log("Running solutions")
        run_solutions(problem_obj, cpu_number)
        print_to_html(problem_obj)
    if grader:
        delete_grader_tmp_folder(problem_obj)


def get_encoded_tests(folder: str) -> Dict[str, bytes]:
    """
    Get a dictionary of encoded test files from a input folder.

    Args:
        folder: Path to the tests folder.

    Returns:
        A dictionary which contains the encoded version of the input files in bytes (key) 
        and the path to the file.
    """
    files: list = [f for f in os.listdir(
        folder) if not f.endswith('.interactive')]
    files.sort(key=custom_key)
    files_path: list = [os.path.join(folder, f) for f in files]
    return encode_tests(files_path)


def encode_tests(files: list) -> Dict[str, bytes]:
    """
    Generates a dictionary of SHA-1 hash values of input file.

    Args:
        files: List containing paths to input files.

    Returns:
        A dictionary which contains the encoded version of the input files in bytes.
    """
    tests = dict()
    for fname in files:
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
    input_files = [f for f in os.listdir(
        input_folder) if not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    input_files = [os.path.join(input_folder, f) for f in input_files]
    for fpath in input_files:
        with open(fpath) as f:
            p = subprocess.run([validator_path],
                               stdin=f, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            check_subprocess_output(
                p, "Failed validation on input " + os.path.basename(fpath))

    # Check for equal test cases
    equal_tests = 0
    encoded_tests = encode_tests(input_files)
    for key in encoded_tests:
        if len(encoded_tests[key]) > 1:
            equal_tests += len(encoded_tests[key])
            debug_log("Testcases " +
                      ', '.join(encoded_tests[key]) + " are equal.")
    if equal_tests:
        warning_log(
            f"There are {equal_tests} equal tests. Check debug.log for more information.")


def move_inputs(temporary_folder: str) -> None:
    """
    Move input tests to the problem folder.

    Args:
        temporary_folder: Path to the temporary input folder.
    """
    problem_dir = Paths().get_problem_dir()
    input_folder: str = os.path.join(problem_dir, 'input')

    # Reset input folder
    for file in os.listdir(input_folder):
        if not file.endswith('.interactive'):
            os.remove(os.path.join(input_folder, file))

    # Move tests to problem folder
    for f in os.listdir(temporary_folder):
        shutil.copy2(os.path.join(temporary_folder, f),
                     os.path.join(input_folder, f.lstrip('0')))


def generate_inputs(move: bool = True, output_folder: str = '') -> None:
    """Generate input tests of the problem in a temporary folder.

    Args:
        move: Whether to move the input tests to the problem folder.
        output_folder: Path to the output folder.
    """
    info_log("Generating input tests in temporary folder.")
    problem_dir = Paths().get_problem_dir()
    bin_folder = os.path.join(problem_dir, 'bin')
    script_path: str = os.path.join(problem_dir, 'src', 'script.sh')
    verify_path(bin_folder)
    verify_path(script_path)

    # Create temporary folder for input tests
    if output_folder == '':
        output_folder = os.path.join(Paths().get_tmp_output_dir(), 'scripts')
    temporary_folder = os.path.join(output_folder, 'tmp')
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(temporary_folder, exist_ok=True)

    # Get scripts for generators
    scripts: list = []
    with open(script_path, 'r') as f:
        scripts: list = f.readlines()

    index: int = 1
    new_script = []
    file_gen: set = set()
    generator_index: list = []

    cwd = os.getcwd()
    for script in scripts:
        # Verify generator path
        script_args = script.split()
        if len(script_args) == 0:
            continue
        script_args[0] = os.path.join(bin_folder, script_args[0].rstrip())
        verify_path(script_args[0])
        if script_args[0] in file_gen:
            continue

        # Generate testcase(s) in temporary folder
        os.chdir(temporary_folder)
        p: subprocess.CompletedProcess = subprocess.run(
            [*script_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        script_result: str = p.stdout
        p.stdout = ""
        check_subprocess_output(p, "Error generating inputs.")
        os.chdir(cwd)

        new_script.append(script)
        generator_index.append(len(os.listdir(temporary_folder)))
        # If it is not a multigenerator, create test in script folder
        if len(os.listdir(temporary_folder)) == 0:
            with open(os.path.join(output_folder, str(index).zfill(3)), 'w') as input_file:
                input_file.write(script_result)
                index += 1
        # If it is a multigenerator, move tests to script folder
        else:
            file_gen.add(script_args[0])
            files = os.listdir(temporary_folder)
            files.sort(key=custom_key)
            for file in files:
                shutil.move(os.path.join(temporary_folder, file),
                            os.path.join(output_folder, str(index).zfill(3)))
                index += 1
    os.rmdir(temporary_folder)

    if new_script != scripts:
        info_log("Rearraging generators order in script.sh")
        with open(script_path, 'w') as f:
            f.writelines(new_script)

    # Write quantity of tests generated by each generator
    with open(os.path.join(os.path.dirname(output_folder), 'index_gen'), 'w') as f:
        f.write('\n'.join(map(str, generator_index)))

    # Move inputs to problem folder
    move_inputs(output_folder) if move else None


def produce_outputs(problem_obj: Problem, problem_metadata: dict) -> None:
    """
    Run main solution on inputs to produce the outputs.

    Args:
        problem_metadata: Dictionary containing the values of problem.json.
    """
    info_log("Producing outputs")
    problem_dir = Paths().get_problem_dir()
    input_folder = os.path.join(problem_dir, 'input')
    output_folder = os.path.join(problem_dir, 'output')
    input_files: list = [f for f in os.listdir(input_folder)
                         if not f.endswith('.interactive')]
    main_solution = Solution(
        problem_metadata["solutions"]["main-ac"], 'main-ac')
    command = identify_language(problem_obj, main_solution).split()

    if problem_metadata["problem"]["interactive"]:
        tmp_fifo = os.path.join(output_folder, 'tmpfifo')
        if os.path.exists(tmp_fifo):
            info_log("Removing existing FIFO")
            subprocess.run(['rm', tmp_fifo])
        subprocess.run(['mkfifo', tmp_fifo])

    for fname in input_files:
        inf_path: str = os.path.join(input_folder, fname)
        ouf_path: str = os.path.join(output_folder, fname)
        with open(inf_path, 'r') as inf, open(ouf_path, 'w') as ouf:
            if problem_metadata["problem"]["interactive"]:
                interactor: str = os.path.join(
                    problem_dir, 'bin', 'interactor')
                verify_path(interactor)
                command: list = [interactor, inf_path, ouf_path, '<',
                                 tmp_fifo, '|', *command, '>', tmp_fifo]
                p = subprocess.Popen(
                    ' '.join(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                p.wait()
            else:
                p = subprocess.run(command, stdin=inf,
                                   stdout=ouf, stderr=subprocess.PIPE)
            check_subprocess_output(
                p, f"Generation of output failed for input {fname}")

    if problem_metadata["problem"]["interactive"]:
        subprocess.run(['rm', tmp_fifo])
    info_log("Outputs produced in problem folder.")


def clean_files() -> None:
    """Call Makefile in order to remove executables."""
    old_cwd: str = os.getcwd()
    os.chdir(Paths().get_problem_dir())
    verify_path('Makefile')

    command: list = ['make', 'clean']
    p: subprocess.CompletedProcess = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check_subprocess_output(p, "Error cleaning executables.")
    os.chdir(old_cwd)


def parse_solutions(problem_obj: Problem, solutions: dict, all_solutions, specific_solution: str, grader: bool) -> None:
    """Parse the solutions from the problem.json file.

    Args:
        problem_obj: Problem object.
        solutions: Dictionary containing the solutions from the problem.json file.
        all_solutions: Boolean indicating whether to run all solution files.
        specific_solution: String containing name of the solution to run.
    """
    solution: Solution = None
    if all_solutions:
        for expected_result, files in solutions.items():
            if len(files) == 0:
                continue
            if isinstance(files, list):
                for submission_file in files:
                    solution = Solution(submission_file, expected_result)
                    solution.exec_args = identify_language(
                        problem_obj, solution, grader)
                    problem_obj.add_solution(solution)
            else:
                submission_file = files
                solution = Solution(submission_file, expected_result)
                solution.exec_args = identify_language(
                    problem_obj, solution, grader)
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
                            solution.exec_args = identify_language(
                                problem_obj, solution, grader)
                            problem_obj.add_solution(solution)
                else:
                    submission_file = files
                    if submission_file == specific_solution:
                        solution = Solution(submission_file, expected_result)
                        solution.exec_args = identify_language(
                            problem_obj, solution, grader)
                        problem_obj.add_solution(solution)

            if problem_obj.is_solution_list_empty():
                error_log(f'Solution {specific_solution} not found.')
        else:
            expected_result = "main-ac"
            submission_file = solutions[expected_result]
            solution = Solution(submission_file, expected_result)
            solution.exec_args = identify_language(
                problem_obj, solution, grader)
            problem_obj.add_solution(solution)

    return


def identify_language(problem_obj: Problem, solution: Solution, grader: bool = False) -> str:
    """
    Identifies the programming language of the solution and returns the appropriate command-line arguments.

    Args:
        problem_obj: The problem being solved.
        solution: The solution to the problem.
        grader: Boolean indicating whether the problem is a grader.

    Returns:
        str: The command-line arguments needed to execute the solution.
    """
    binary_file: str = solution.get_binary_name()
    ext: str = solution.get_file_extension()
    problem_folder = problem_obj.problem_dir
    bin_folder = os.path.join(problem_folder, 'bin')
    src_folder = os.path.join(problem_folder, 'src')
    exec_args: str = None

    if (ext == 'cpp' or ext == 'c'):
        exec_args = os.path.join(bin_folder, binary_file)
    elif (ext == 'java'):
        exec_args = f'{JAVA_INTERPRETER} {JAVA_FLAG} {bin_folder} {solution.get_binary_name()}'
    elif (ext == 'py'):
        if grader:
            prepare_grader_solution(src_folder, solution)
            submission_file = os.path.join(
                src_folder, binary_file, solution.solution_name)
        else:
            submission_file = os.path.join(
                src_folder, solution.solution_name)
        exec_args = f'{PYTHON3_INTERPRETER} {submission_file}'
    else:
        error_log(f'{solution.solution_name} has an invalid extension.')

    return exec_args


def prepare_grader_solution(src_folder: str, solution: Solution) -> str:
    grader_folder: str = os.path.join(
        src_folder, solution.get_binary_name())
    grader_files: list[str] = ['main.py', solution.solution_name]
    copy_files(src_folder, grader_folder, grader_files)
    os.rename(os.path.join(grader_folder, solution.solution_name),
              os.path.join(grader_folder, 'solution.py'))
    os.rename(os.path.join(grader_folder, 'main.py'), os.path.join(
        grader_folder, solution.solution_name))


def delete_grader_tmp_folder(problem: Problem) -> None:
    solutions: list[Solution] = problem.get_list_solution()
    for solution in solutions:
        if solution.get_file_extension() == 'py':
            grader_folder: str = os.path.join(
                problem.problem_dir, 'src', solution.get_binary_name())
            shutil.rmtree(grader_folder)
