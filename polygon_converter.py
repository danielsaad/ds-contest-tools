import io
import os
import json
import shutil
import zipfile
import requests
import xml.etree.ElementTree as ET
from metadata import Paths
from utils import instance_paths
from jsonutils import parse_json
from fileutils import get_statement_files
from polygon_submitter import add_auth_parameters, verify_response


DEFAULT_LANGUAGE = 'english'


def get_text(filename, language=DEFAULT_LANGUAGE):
    """Get statement texts from the Polygon package."""
    package_folder = Paths.instance().dirs['output_dir']
    filename = os.path.join(
        *[package_folder, 'statement-sections', language, filename])
    if not os.path.isfile(filename):
        return ''
    with open(filename, 'r') as fh:
        text = fh.readlines()
    return text


def get_statement(language=DEFAULT_LANGUAGE):
    return get_text('legend.tex', language)


def get_input_description(language=DEFAULT_LANGUAGE):
    return get_text('input.tex', language)


def get_output_description(language=DEFAULT_LANGUAGE):
    return get_text('output.tex', language)


def get_notes(language=DEFAULT_LANGUAGE):
    return get_text('notes.tex', language)


def get_tutorial(language=DEFAULT_LANGUAGE):
    return get_text('tutorial.tex', language)


def get_title(language=DEFAULT_LANGUAGE):
    return get_text('name.tex', language)


def get_interaction(language=DEFAULT_LANGUAGE):
    return get_text('interaction.tex', language)


def get_input_list() -> list:
    """Get list of input files from the package."""
    package_folder = Paths.instance().dirs['output_dir']
    input_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(input_folder, x) for x in os.listdir(
        input_folder) if not x.endswith('.a')]
    return file_list


def get_output_list() -> list:
    """Get list of output files from the package."""
    package_folder = Paths.instance().dirs['output_dir']
    output_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(output_folder, x)
                 for x in os.listdir(output_folder) if x.endswith('.a')]
    return file_list


def get_interactive_list() -> list:
    """Get list of interactive I/O files of the statement from the package."""
    package_folder = Paths.instance().dirs['output_dir']
    interactive_folder = os.path.join(
        *[package_folder, 'statements', 'english'])
    file_list = [os.path.join(interactive_folder, x)
                 for x in os.listdir(interactive_folder) if x.startswith('example.')]
    return file_list


def copy_input_files() -> None:
    """Copy input files from the package to the problem folder."""
    problem_folder = Paths.instance().dirs['problem_dir']
    file_list = get_input_list()
    destination = os.path.join(problem_folder, 'input')
    for filepath in file_list:
        new_filename = os.path.basename(filepath).lstrip('0')
        shutil.copy(filepath, os.path.join(destination, new_filename))


def copy_output_files() -> None:
    """Copy output files from the package to the problem folder."""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']
    file_list = get_output_list()
    destination = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        new_filename = os.path.splitext(
            os.path.basename(filepath))[0].lstrip('0')
        new_filepath = os.path.join(destination, new_filename)
        shutil.copy(filepath, new_filepath)


def copy_interactive_files() -> None:
    """Copy interactive statement files from the package to the problem folder."""
    problem_folder = Paths.instance().dirs['problem_dir']
    file_list = get_interactive_list()
    destination_input = os.path.join(problem_folder, 'input')
    destination_output = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        destination = destination_output if filepath.endswith(
            '.a') else destination_input
        new_filename = os.path.basename(filepath).lstrip(
            'example.').lstrip('0').rstrip('.a') + '.interactive'
        shutil.copy(filepath, os.path.join(destination, new_filename))


def copy_validator() -> None:
    """Copy validator from package to problem folder."""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']
    validator = os.path.join(*[package_folder, 'files', 'validator.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'validator.cpp'])
    shutil.copy(validator, destination)


def copy_generator(script) -> None:
    """Copy generators from package to problem folder."""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']
    for file in os.listdir(os.path.join(package_folder, 'files')):
        if not file.startswith('generator'):
            continue
        generator = os.path.join(*[package_folder, 'files', file])
        destination = os.path.join(*[problem_folder, 'src', file])
        shutil.copy(generator, destination)

    if script != '':
        with open(os.path.join(*[problem_folder, 'src', 'script.sh']), 'w') as f:
            f.write(script)


def copy_source_files(file_name: str) -> None:
    """Copy source files from package to problem folder."""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']
    checker = os.path.join(*[package_folder, 'files', file_name])
    destination = os.path.join(*[problem_folder, 'src', file_name])
    shutil.copy(checker, destination)


def copy_solutions() -> None:
    """Copy solution files from package to problem folder."""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']
    solution_folder = os.path.join(package_folder, 'solutions')

    source_files = [os.path.join(solution_folder, x) for x in os.listdir(
        solution_folder) if not x.endswith('.desc')]
    destination = os.path.join(problem_folder, 'src')
    for f in source_files:
        shutil.copy(f, destination)


def verify_interactive(problem_id: str) -> bool:
    content = get_polygon_response(dict(), 'problem.info', problem_id)
    content = json.loads(content)
    return content['result']['interactive']


def init_problem(interactive: bool) -> None:
    """Initialize problem folder before the conversion."""
    tool_path = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(tool_path, 'arquivos')
    problem_folder = Paths.instance().dirs['problem_dir']

    shutil.copytree(folder, problem_folder,
                    ignore=shutil.ignore_patterns('boca', 'src'),
                    dirs_exist_ok=True)
    os.makedirs(os.path.join(problem_folder, 'src'), exist_ok=True)
    os.makedirs(os.path.join(problem_folder, 'input'), exist_ok=True)
    os.makedirs(os.path.join(problem_folder, 'output'), exist_ok=True)
    shutil.copy(os.path.join(*[folder, 'src', 'testlib.h']), os.path.join(problem_folder, 'src'))
    os.remove(os.path.join(problem_folder, 'problem-interactive.json'))
    if not interactive:
        os.remove(os.path.join(
            *[problem_folder, 'statement', 'interactor.tex']))


def write_statement(package_data: dict, interactive: bool) -> None:
    """Write statement files in the problem folder."""
    problem_folder = Paths.instance().dirs['problem_dir']
    statement_dir = os.path.join(problem_folder, 'statement')

    statement_files = get_statement_files(statement_dir, interactive)
    with open(statement_files[0], 'w') as f:
        [print(line, file=f, end='') for line in package_data['statement']]
    with open(statement_files[1], 'w') as f:
        [print(line, file=f, end='')
         for line in package_data['input_description']]
    with open(statement_files[2], 'w') as f:
        [print(line, file=f, end='')
         for line in package_data['output_description']]
    with open(statement_files[3], 'w') as f:
        [print(line, file=f, end='') for line in package_data['notes']]
    with open(statement_files[4], 'w') as f:
        [print(line, file=f, end='') for line in package_data['tutorial']]
    if interactive:
        with open(statement_files[5], 'w') as f:
            [print(line, file=f, end='')
             for line in package_data['interaction']]


def get_package_data(interactive: bool) -> dict:
    """Get statement information from package."""
    problem_data = {}
    problem_data['title'] = get_title()
    problem_data['statement'] = get_statement()
    problem_data['input_description'] = get_input_description()
    problem_data['output_description'] = get_output_description()
    problem_data['notes'] = get_notes()
    problem_data['tutorial'] = get_tutorial()
    if interactive:
        problem_data['interaction'] = get_interaction()
    return problem_data


def get_scripts_xml(root) -> str:
    """Get generator scripts used to create inputs."""
    gen_scripts = ''
    for tests in root.findall('./judging/testset/tests/test'):
        script = tests.get('cmd')
        if script is not None:
            gen_scripts += script + '\n'
    return gen_scripts


def get_solution_tags() -> dict:
    """Get dictionary with every solution tag possible."""
    tags = {
        'main': 'main-ac',
        'failed': 'runtime-error',
        'rejected': 'runtime-error',
        'accepted': 'alternative-ac',
        'wrong-answer': 'wrong-answer',
        'memory-limit-exceeded': 'memory-limit',
        'presentation-error': 'presentation-error',
        'time-limit-exceeded': 'time-limit',
        'time-limit-exceeded-or-accepted': 'time-limit-or-ac',
        'time-limit-exceeded-or-memory-limit-exceeded': 'time-limit-or-memory-limit'
    }
    return tags


def get_solutions_xml(root) -> dict:
    """Parse solution files from XML."""
    solutions = dict()
    tags = get_solution_tags()
    for data in root.findall('./assets/solutions/solution'):
        solution_tag = data.get('tag')
        if solution_tag is None:
            continue

        for filename in data.findall('source'):
            # Add solution to list inside the dictionary
            name = filename.get('path')
            if name is not None:
                solutions.setdefault(tags[solution_tag], []).append(
                    os.path.basename(name))
    # Convert main solution to a string
    solutions['main-ac'] = ''.join(solutions['main-ac'])
    return solutions


def get_data_xml() -> dict:
    """Get scripts and solutions from the package XML file."""
    package_folder = Paths.instance().dirs['output_dir']
    tree = ET.parse(os.path.join(package_folder, 'problem.xml'))
    root = tree.getroot()

    xml_data = {}
    xml_data['script'] = get_scripts_xml(root)
    xml_data['solutions'] = get_solutions_xml(root)
    return xml_data


def get_tags() -> dict:
    """Get tags of the problem."""
    package_folder = Paths.instance().dirs['output_dir']
    tags = {'en_us': list()}
    with open(os.path.join(package_folder, 'tags'), 'r') as f:
        for line in f.readlines():
            tags['en_us'].append(line.rstrip())
    return tags


def update_problem_json(title, solutions, interactive) -> None:
    """Update problem information from the package"""
    package_folder = Paths.instance().dirs['output_dir']
    problem_folder = Paths.instance().dirs['problem_dir']

    # Get informations of the problem
    tags = get_tags()
    json_path = os.path.join(problem_folder, 'problem.json')
    package_json = parse_json(os.path.join(
        *[package_folder, 'statements', 'english', 'problem-properties.json']))
    problem_json = parse_json(json_path)

    # Update problem.json
    problem_json['problem']['subject'] = tags
    problem_json['problem']['interactive'] = interactive
    problem_json['io_samples'] = len(package_json['sampleTests'])
    problem_json['problem']['title'] = ''.join(title).rstrip()
    problem_json['problem']['input_file'] = package_json['inputFile']
    problem_json['problem']['output_file'] = package_json['outputFile']
    problem_json['problem']['time_limit'] = int(
        package_json['timeLimit'] / 1000)
    problem_json['problem']['memory_limit_mb'] = int(
        (package_json['memoryLimit'] / 1024) / 1024)
    for key in solutions:
        problem_json['solutions'][key] = solutions[key]

    with open(json_path, 'w') as f:
        f.write(json.dumps(problem_json, ensure_ascii=False))


def convert_problem(local, problem_id):
    """Convert package from Polygon to DS."""
    xml_data = get_data_xml()
    interactive = verify_interactive(problem_id)
    package_data = get_package_data(interactive)

    # Copy data from package to problem folder
    init_problem(interactive)
    copy_input_files()
    copy_output_files()
    copy_solutions()
    copy_source_files('checker.cpp')
    copy_source_files('validator.cpp')
    copy_source_files('interactor.cpp')
    if interactive:
        copy_interactive_files()

    write_statement(package_data, interactive)
    copy_generator(xml_data['script'])
    update_problem_json(package_data['title'],
                        xml_data['solutions'], interactive)
    if not local:
        shutil.rmtree(Paths.instance().dirs['output_dir'])


def get_package_id(packages: dict) -> int:
    """Get ID from the latest READY linux package."""
    recent = 0
    package_id = -1
    for package in packages:
        if package['state'] != 'READY':
            continue
        if package['type'] != 'linux':
            continue
        if package['creationTimeSeconds'] < recent:
            continue
        package_id = package['id']
        recent = package['creationTimeSeconds']
    if (package_id == -1):
        print("There is no package READY.")
        exit(1)
    return package_id


def get_polygon_response(params, method, problem_id):
    """Make connection Polygon API."""
    tool_path = os.path.dirname(os.path.abspath(__file__))

    keys = parse_json(os.path.join(tool_path, 'secrets.json'))
    params = add_auth_parameters(method, params, problem_id, keys)

    url = 'https://polygon.codeforces.com/api/'
    response = requests.post(url + method, files=params)
    verify_response(response, method)
    return response.content


def download_package_polygon(problem_id):
    """Download zip package from Polygon."""
    content = json.loads(get_polygon_response(
        dict(), 'problem.packages', problem_id))

    # Get the correct package
    package_id = get_package_id(content['result'])

    # Get bytes of the package
    params = dict()
    params['packageId'] = package_id
    params['type'] = 'linux'
    response = get_polygon_response(params, 'problem.package', problem_id)

    # Convert bytes to zip file
    package = zipfile.ZipFile(io.BytesIO(response))
    package.extractall(Paths.instance().dirs['output_dir'])
    package.close()


def get_polygon_problem(problem_folder, local):
    """Verify source from problem package and convert it."""
    problem_id = input('ID: ')
    if local:
        if not os.path.exists(local):
            print(f"{local} problem does not exist.")
            exit(1)
        instance_paths(problem_folder, local)
    else:
        instance_paths(problem_folder, os.path.join(
                       problem_folder, 'temp_package'))
        download_package_polygon(problem_id)
    convert_problem(local, problem_id)
