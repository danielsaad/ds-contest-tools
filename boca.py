import os
import subprocess
import glob
import shutil
from fileutils import recursive_overwrite
from jsonutils import parse_json


class default_boca_limits:
    time_limit = 1  # time limit for all tests
    number_of_repetitions = 1  # number of repetitions
    maximum_memory = 512  # Maximum memory size (MB)
    maximum_output_size = 4096  # Maximum output size (KB)


def boca_zip(boca_folder):
    old_cwd = os.getcwd()
    os.chdir(boca_folder)
    zip_filename = os.path.basename(boca_folder)+'.zip'
    subprocess.run('zip'+' -r ' + zip_filename + ' . ', shell=True)
    os.rename(zip_filename, os.path.join('..', zip_filename))
    os.chdir(old_cwd)


def boca_pack(problem_folder):
    boca_template_folder = os.path.join(
        *[os.path.dirname(os.path.abspath(__file__)), 'arquivos', 'boca'])
    boca_folder = os.path.join(*[problem_folder, 'boca'])
    # Copy template files
    recursive_overwrite(boca_template_folder, boca_folder)
    # Get problem metadata
    problem_md = glob.glob(os.path.join(problem_folder, '*.md'))[0]
    tl = 0
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    # with open(problem_md) as f:
    #     # Compile, Run and Tests Remains the Same

    #     # Description
    boca_description_folder = os.path.join(boca_folder, 'description')
    with open(os.path.join(boca_description_folder, 'problem.info'), 'w+') as f:
        f.write('basename='+problem_metadata['problem']['label']+'\n')
        f.write('fullname='+problem_metadata['problem']['label']+'\n')
        f.write('descfile='+problem_metadata['problem']['label']+'.pdf\n')

    pdf_file = os.path.join(
        problem_folder, problem_metadata['problem']['label']+'.pdf')
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
            if(filename in ['java', 'py2', 'py3']):
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
    print('input_files = ', ' '.join(input_files))
    for filename in input_files:
        shutil.copy2(filename, boca_input_folder)

    # Output
    boca_output_folder = os.path.join(boca_folder, 'output')
    problem_output_folder = os.path.join(problem_folder, 'output')
    os.makedirs(boca_output_folder, exist_ok=True)
    output_files = [os.path.join(problem_output_folder, f) for
                    f in os.listdir(problem_output_folder) if os.path.isfile(os.path.join(problem_output_folder, f))]
    print('output_files = ', ' '.join(output_files))
    for filename in output_files:
        shutil.copy2(filename, boca_output_folder)
    boca_zip(boca_folder)
