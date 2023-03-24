import hashlib
import os
import subprocess
import sys

from checker import run_solutions
from config import custom_key
from htmlutils import print_to_html
from jsonutils import parse_json
from logger import debug_log, error_log, info_log
from metadata import Paths
from utils import check_subprocess_output, verify_path, check_problem_metadata


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


def run_programs(all_solutions) -> None:
    """Run the executables to create the problem."""
    problem_folder = Paths().get_problem_dir()
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)

    old_cwd = os.getcwd()
    os.chdir(input_folder)
    generate_inputs()
    validate_inputs()
    os.chdir(old_cwd)
    os.chdir(output_folder)
    produce_outputs(problem_metadata)
    os.chdir(old_cwd)
    info_log("Running solutions")
    solutions_info_dict: dict = run_solutions(input_folder, problem_metadata, all_solutions)
    print_to_html(problem_metadata, solutions_info_dict)



def encode_tests(input_files: list) -> dict:
    """Generates hash dictionary of the content of input files."""
    tests = dict()
    for fname in input_files:
        with open(fname, 'rb') as f:
            encoded = (hashlib.sha1(f.read())).digest()
        if encoded in tests:
            tests[encoded].append(fname)
        else:
            tests[encoded] = [fname]
    return tests


def validate_inputs() -> None:
    """Checks if the input files are correctly formatted 
    by running the validator file.
    """
    validator_path = os.path.join('..', 'bin', 'validator')
    verify_path(validator_path)

    input_files = [f for f in os.listdir() if os.path.isfile(f)
                   and not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    for fname in input_files:
        with open(fname) as f:
            p = subprocess.Popen([validator_path],
                                 stdin=f, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            out, err = p.communicate()
            if (out or err):
                error_log(out)
                error_log(err)
                print("Failed validation on input", fname)
                exit(1)

    equal_tests = 0
    encoded_tests = encode_tests(input_files)
    for key in encoded_tests:
        if len(encoded_tests[key]) > 1:
            equal_tests += len(encoded_tests[key])
            info_log("Testcases " +
                     ', '.join(encoded_tests[key]) + " are equal.")

    if (equal_tests):
        print("All test cases must be different, however there are " +
              f"{equal_tests} equal tests.")
        sys.exit(0)


def generate_inputs() -> None:
    """Generates input files from the generator file."""
    scripts = []
    ds_generator = True
    script_path = os.path.join('..', 'src', 'script.sh')
    generator_path = os.path.join('..', 'bin', 'generator')

    # Verify existance of at least one generator
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            scripts = f.readlines()

        for script in scripts:
            if script.startswith('generator '):
                ds_generator = False
                break
    elif not os.path.exists(generator_path):
        print("Error. No generators or scripts found.")
        sys.exit(1)

    # Verify and run a DS generator
    if ds_generator and os.path.exists(generator_path):
        info_log("Generating inputs of generator")
        p = subprocess.run(generator_path, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
        check_subprocess_output(p, "Error generating inputs.")

    # Prepare input for script generation
    input_files = [f for f in os.listdir() if os.path.isfile(f)
                   and not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    encoded_tests = encode_tests(input_files)

    index = len(input_files) + 1
    for script in scripts:
        debug_log(f"Generating script '{script.rstrip()}'.")
        script = script.split()
        generator_path = os.path.join(*['..', 'bin', script[0]])
        verify_path(generator_path)

        script[0] = generator_path
        p = subprocess.run([*script], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
        script_result = p.stdout
        p.stdout = ""
        check_subprocess_output(p, "Error generating inputs.")

        temp_test = hashlib.sha1(script_result.encode()).digest()
        if temp_test in encoded_tests:
            debug_log(f"Script generated repeated testcase. Ignoring...")
            continue
        encoded_tests[temp_test] = script
        debug_log(f"Script generated successfully.")
        info_log(f"Generating testcase {index} from script.")
        with open(str(index), 'w') as input_file:
            input_file.write(script_result)
        index += 1


def produce_outputs(problem_metadata) -> None:
    """Run AC solution on inputs to produce the outputs."""
    info_log("Producing outputs")
    # change cwd to output folder
    input_files = [f for f in os.listdir(os.path.join('..', 'input'))
                   if not f.endswith('.interactive')]
    for fname in input_files:
        inf_path = os.path.join('..', 'input', fname)
        ouf_path = fname
        with open(os.path.join('..', 'input', fname), 'r') as inf, open(fname, 'w') as ouf:
            ac_solution = os.path.join(
                '..', 'bin', os.path.splitext(problem_metadata["solutions"]["main-ac"])[0])
            if (problem_metadata["problem"]["interactive"]):
                interactor = os.path.join('..', 'bin', 'interactor')
                verify_path(interactor)

                if os.path.exists('tmpfifo'):
                    info_log("Removing existing FIFO")
                    subprocess.run(['rm', 'tmpfifo'])
                subprocess.run(['mkfifo', 'tmpfifo'])

                command = [interactor, inf_path, ouf_path, '<',
                           'tmpfifo', '|', ac_solution, '>', 'tmpfifo']

                p = subprocess.run(' '.join(command),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                subprocess.run(['rm', 'tmpfifo'])
            else:
                p = subprocess.run([ac_solution], stdin=inf, stdout=ouf,
                                   stderr=subprocess.PIPE, text=True, encoding='utf-8')
            check_subprocess_output(p, f"Generation of output failed for input {fname}")
    info_log("Outputs produced successfully.")


def clean_files() -> None:
    """
    Call Makefile in order to remove executables
    """
    old_cwd = os.getcwd()
    os.chdir(Paths().get_problem_dir())
    verify_path('Makefile')

    command = ['make', 'clean']
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    check_subprocess_output(p, "Error cleaning executables.")

    os.chdir(old_cwd)
