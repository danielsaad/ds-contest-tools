import os
import sys
import hashlib
import subprocess
from metadata import Paths
from config import custom_key
from jsonutils import parse_json
from utils import verify_command
from checker import run_solutions
from logger import info_log, error_log


def build_executables() -> None:
    """Run Makefile to create release and debug executables."""
    old_cwd = os.getcwd()
    os.chdir(Paths.instance().dirs["problem_dir"])

    info_log("Compiling executables")
    p = subprocess.run(['make', '-j'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    verify_command(p, "Makefile failed.")
    os.chdir(old_cwd)


def run_programs(all_solutions) -> None:
    """Run the executables to create the problem."""
    problem_folder = Paths.instance().dirs["problem_dir"]
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))

    old_cwd = os.getcwd()
    os.chdir(input_folder)
    generate_inputs()
    validate_inputs()
    os.chdir(old_cwd)
    os.chdir(output_folder)
    produce_outputs(problem_metadata)
    os.chdir(old_cwd)
    info_log("Running solutions")
    run_solutions(input_folder, problem_metadata, all_solutions)


def validate_inputs() -> None:
    """Checks if the input files are correctly formatted 
    by running the validator file.
    """
    input_files = [f for f in os.listdir() if os.path.isfile(f)
                   and not f.endswith('.interactive')]
    input_files.sort(key=custom_key)
    for fname in input_files:
        with open(fname) as f:
            p = subprocess.Popen([os.path.join('../bin', 'validator')],
                                 stdin=f, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            out, err = p.communicate()
            if (out or err):
                error_log(out)
                error_log(err)
                print("Failed validation on input.", fname)
                exit(1)

    tests = dict()
    for fname in input_files:
        with open(fname, 'rb') as f:
            encoded = (hashlib.sha1(f.read())).digest()
        if encoded in tests:
            tests[encoded].append(fname)
        else:
            tests[encoded] = [fname]
    equal_tests = 0
    for key in tests:
        if len(tests[key]) > 1:
            equal_tests += len(tests[key])
            info_log("Testcases " + ', '.join(tests[key]) + " are equal.")

    if (equal_tests):
        print("All test cases must be different, however there are " +
              f"{equal_tests} equal tests.")
        sys.exit(0)


def generate_inputs() -> None:
    """Generates input files from the generator file."""
    scripts = []
    ds_generator = True
    script_path = os.path.join('../src', 'script.sh')
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            scripts = f.readlines()

        for script in scripts:
            if script.startswith('generator '):
                ds_generator = False
                break

    if ds_generator:
        generator_command = os.path.join('../bin', 'generator')
        info_log('Generating inputs of generator')
        p = subprocess.run(generator_command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
        verify_command(p, "Error generating inputs.")

    index = len(os.listdir()) + 1
    for script in scripts:
        info_log(f'Generating {index} testcase from script')
        
        script = script.split()
        generator_path = os.path.join('../bin', script[0])
        if not os.path.exists(generator_path):
            print(f'Generator {os.path.basename(generator_path)} does not exist.')
            sys.exit(1)

        script[0] = os.path.join('../bin', script[0])
        p = subprocess.run([*script], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True)
        verify_command(p, "Error generating inputs.")
        with open(str(index), 'w') as input_file:
            input_file.write(p.stdout)
        index += 1


def produce_outputs(problem_metadata) -> None:
    """Run AC solution on inputs to produce the outputs."""
    info_log("Producing outputs")
    # change cwd to output folder
    input_files = os.listdir('../input')
    for fname in input_files:
        inf_path = os.path.join('../input', fname)
        ouf_path = fname
        with open(os.path.join('../input', fname), 'r') as inf, open(fname, 'w') as ouf:
            ac_solution = os.path.join('../bin', 'ac')
            if (problem_metadata["problem"]["interactive"]):
                interactor = os.path.join('../bin/interactor')
                # TODO: do this in a more pythonic way
                if (os.path.isfile('tmpfifo')):
                    print("Removing existant FIFO")
                    subprocess.run(['rm', 'tmpfifo'])
                subprocess.run(['mkfifo', 'tmpfifo'])
                command = interactor + ' ' + inf_path + ' ' + ouf_path + \
                    ' < tmpfifo | ' + ac_solution + ' > tmpfifo'
                p = subprocess.run(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True, text=True)
                p1 = subprocess.run(['rm', 'tmpfifo'], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
                verify_command(p1, "Error removing temporary files.")
            else:
                p = subprocess.Popen([ac_solution], stdin=inf, stdout=ouf,
                                     stderr=subprocess.PIPE, text=True, encoding='utf-8')
                _, err = p.communicate()
            if (p.returncode):
                print("Generation of output for input", fname, "failed")
                sys.exit(1)


def clean_files() -> None:
    """Call Makefile in order to remove executables"""
    old_cwd = os.getcwd()
    os.chdir(Paths.instance().dirs["problem_dir"])

    command = ['make', 'clean']
    p = subprocess.run(command, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    verify_command(p, "Error cleaning executables.")

    os.chdir(old_cwd)
