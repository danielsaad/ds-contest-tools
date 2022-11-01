from asyncio import SubprocessProtocol
import os
import subprocess
import sys
from config import custom_key
from jsonutils import parse_json
from polygon_converter import check
from metadata import Paths


def build_executables():
    old_cwd = os.getcwd()
    os.chdir(Paths.instance().dirs["problem_dir"])
    
    # run makefile for release
    print("-Compiling executables")
    p = subprocess.run(['make'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if(p.returncode):
        print("Makefile failed.")
        sys.exit(1)
    os.chdir(old_cwd)

def run_programs():
    problem_folder = Paths.instance().dirs["problem_dir"]
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    # Create input and output folders
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    # store old cwd
    old_cwd = os.getcwd()
    os.chdir(input_folder)
    generate_inputs()
    validate_inputs()
    os.chdir(old_cwd)
    os.chdir(output_folder)
    produce_outputs(problem_metadata)
    os.chdir(old_cwd)


def validate_inputs():
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


def generate_inputs():
    generator_command = os.path.join('../bin', 'generator')
    print('-Generating inputs')
    subprocess.run(generator_command)


def produce_outputs(problem_metadata):
    print("-Producing outputs")
    # change cwd to output folder
    # Run ac solution on inputs to produce outputs
    input_files = os.listdir('../input')
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
