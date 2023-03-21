import os
import sys
import shutil
import subprocess
from metadata import Paths
from utils import verify_command, verify_problem_json
from jsonutils import parse_json
from fileutils import recursive_overwrite, rename_io


class default_boca_limits:
    time_limit = 1  # time limit for all tests
    number_of_repetitions = 1  # number of repetitions
    maximum_memory = 512  # Maximum memory size (MB)
    maximum_output_size = 4096  # Maximum output size (KB)


def boca_zip(boca_folder: str) -> None:
    """ Zip a problem of BOCA format."""
    old_cwd = os.getcwd()
    os.chdir(boca_folder)
    zip_filename = os.path.basename(boca_folder)+'.zip'
    p = subprocess.run('zip'+' -r ' + zip_filename + ' . ', shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    verify_command(p, "Error ziping boca file.")
    os.rename(zip_filename, os.path.join('..', zip_filename))
    os.chdir(old_cwd)


def boca_pack(problem_folder='') -> None:
    """Convert a DS problem to a BOCA problem."""
    if (problem_folder == ''):
        problem_folder = Paths.instance().dirs["problem_dir"]

    boca_template_folder = os.path.join(
        *[os.path.dirname(os.path.abspath(__file__)), 'arquivos', 'boca'])
    boca_folder = os.path.join(*[problem_folder, 'boca'])
    # Copy template files
    recursive_overwrite(boca_template_folder, boca_folder)
    # Get problem metadata
    tl = 0
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    verify_problem_json(problem_metadata)
    basename = os.path.basename(os.path.abspath(problem_folder))
    filename = os.path.join(problem_folder, basename)
    boca_description_folder = os.path.join(boca_folder, 'description')
    with open(os.path.join(boca_description_folder, 'problem.info'), 'w+') as f:
        f.write('basename='+basename+'\n')
        f.write('fullname='+basename+'\n')
        f.write('descfile='+basename+'.pdf\n')

    pdf_file = filename+'.pdf'
    if not os.path.exists(pdf_file):
        print("Problem PDF doesn't exist.")
        sys.exit(1)
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
            if (filename in ['java', 'py2', 'py3']):
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
    for filename in input_files:
        shutil.copy2(filename, boca_input_folder)
    rename_io(boca_input_folder)

    # Output
    boca_output_folder = os.path.join(boca_folder, 'output')
    problem_output_folder = os.path.join(problem_folder, 'output')
    os.makedirs(boca_output_folder, exist_ok=True)
    output_files = [os.path.join(problem_output_folder, f) for
                    f in os.listdir(problem_output_folder) if os.path.isfile(os.path.join(problem_output_folder, f))]
    for filename in output_files:
        shutil.copy2(filename, boca_output_folder)
    rename_io(boca_output_folder)
    boca_zip(boca_folder)
