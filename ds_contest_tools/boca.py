import os
import shutil
import subprocess

from .fileutils import recursive_overwrite, rename_io
from .jsonutils import parse_json
from .logger import error_log, info_log
from .utils import check_problem_metadata, check_subprocess_output, verify_path


class default_boca_limits:
    number_of_repetitions = 1  # number of repetitions
    maximum_memory = 512  # Maximum memory size (MB)
    maximum_output_size = 4096  # Maximum output size (KB)


def boca_zip(boca_folder: str) -> None:
    """ Zip a problem of BOCA format.
    
    Args:
        boca_folder: Path to the BOCA folder.
    """
    info_log("Zipping BOCA package")
    old_cwd = os.getcwd()
    os.chdir(boca_folder)
    zip_filename = os.path.basename(boca_folder)+'.zip'
    p = subprocess.run('zip'+' -r ' + zip_filename + ' . ', shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check_subprocess_output(p, "Error zipping BOCA file.")
    os.rename(zip_filename, os.path.join('..', zip_filename))
    os.chdir(old_cwd)


def boca_pack(problem_folder: str, output_folder: str) -> None:
    """Convert a DS problem to a BOCA problem.
    
    Args:
        problem_folder: Path to the problem folder.
        output_folder: Path to the output folder.
    """
    # Verify if it is a conversion from a contest
    info_log(f"Starting BOCA conversion for problem {os.path.basename(problem_folder)}.")
    os.makedirs(output_folder, exist_ok=True)

    boca_template_folder = os.path.join(
        *[os.path.dirname(os.path.abspath(__file__)), 'files', 'boca'])
    boca_folder = os.path.join(*[output_folder, 'boca'])
    
    # Copy template files
    recursive_overwrite(boca_template_folder, boca_folder)
    
    # Get problem metadata
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    basename = os.path.basename(os.path.abspath(problem_folder))
    filename = os.path.join(problem_folder, basename)
    boca_description_folder = os.path.join(boca_folder, 'description')
    with open(os.path.join(boca_description_folder, 'problem.info'), 'w+') as f:
        f.write('basename='+basename+'\n')
        f.write('fullname='+basename+'\n')
        f.write('descfile='+basename+'.pdf\n')

    pdf_file = filename+'.pdf'
    verify_path(pdf_file)
    shutil.copy2(pdf_file, boca_description_folder)

    # Compare
    checker_boca = os.path.join(problem_folder, 'bin', 'checker-boca')
    verify_path(checker_boca)
    compare_folder = os.path.join(boca_folder, 'compare')
    checker_compare = os.path.join(compare_folder, 'checker-boca')
    shutil.copy2(checker_boca, checker_compare)
    shutil.copy2(checker_compare, os.path.join(compare_folder, 'c'))
    shutil.copy2(checker_compare, os.path.join(compare_folder, 'cpp'))
    shutil.copy2(checker_compare, os.path.join(compare_folder, 'java'))
    shutil.copy2(checker_compare, os.path.join(compare_folder, 'py2'))
    shutil.copy2(checker_compare, os.path.join(compare_folder, 'py3'))

    # Limits
    java_python_time_factor = 3
    for filename in os.listdir(os.path.join(boca_template_folder, 'limits')):
        with open(os.path.join(*[boca_folder, 'limits', filename]), 'w+') as f:
            time_limit = problem_metadata['problem']['time_limit']
            if filename in ['java', 'py2', 'py3']:
                time_limit *= java_python_time_factor
            
            # Get limits from problem.json or use default values, if not specified
            repetitions = problem_metadata['boca_config']['number_of_repetitions']
            repetitions = repetitions if repetitions is not None else default_boca_limits.number_of_repetitions
            max_memory = problem_metadata['boca_config']['maximum_memory_mb']
            max_memory = max_memory if max_memory is not None else default_boca_limits.maximum_memory
            max_output = problem_metadata['boca_config']['maximum_output_size_kb']
            max_output = max_output if max_output is not None else default_boca_limits.maximum_output_size
            
            f.write('echo ' + str(time_limit) + '\n')
            f.write('echo ' + str(repetitions)+'\n')
            f.write('echo ' + str(max_memory)+'\n')
            f.write('echo ' + str(max_output)+'\n')
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
