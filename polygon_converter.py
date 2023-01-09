# Converts a Linux Package from Polygon to DS format

import io
import os
import json
import time
import shutil
import zipfile
import requests
import argparse
import hashlib
import random
import string
import xml.etree.ElementTree as ET
from build import init
from utils import instance_paths
from logger import info_log, error_log
from jsonutils import parse_json

DEFAULT_LANGUAGE = 'english'


def get_text(package_folder, filename, language=DEFAULT_LANGUAGE):
    filename = os.path.join(
        *[package_folder, 'statement-sections', language, filename])
    if not os.path.isfile(filename):
        return ''
    with open(filename, 'r') as fh:
        text = fh.readlines()
    return text


def get_statement(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'legend.tex', language)


def get_input_description(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'input.tex', language)


def get_output_description(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'output.tex', language)


def get_notes(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'notes.tex', language)


def get_tutorial(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'tutorial.tex', language)


def get_title(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'name.tex', language)


def get_input_list(package_folder):
    input_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(input_folder, x) for x in os.listdir(
        input_folder) if not x.endswith('.a')]
    return file_list


def get_output_list(package_folder):
    output_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(output_folder, x)
                 for x in os.listdir(output_folder) if x.endswith('.a')]
    return file_list


def copy_input_files(package_folder, problem_folder):
    file_list = get_input_list(package_folder)
    destination = os.path.join(problem_folder, 'input')
    for filepath in file_list:
        new_filename = os.path.basename(filepath).lstrip('0')
        shutil.copy(filepath, os.path.join(destination, new_filename))


def copy_output_files(package_folder, problem_folder):
    file_list = get_output_list(package_folder)
    destination = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        new_filename = os.path.splitext(
            os.path.basename(filepath))[0].lstrip('0')
        new_filepath = os.path.join(destination, new_filename)
        shutil.copy(filepath, new_filepath)


def copy_validator(package_folder, problem_folder) -> None:
    """Copy validator from package to problem folder."""
    validator = os.path.join(*[package_folder, 'files', 'validator.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'validator.cpp'])
    shutil.copy(validator, destination)


def copy_generator(package_folder, problem_folder, script) -> None:
    """Copy generator from package to problem folder."""
    generator = os.path.join(*[package_folder, 'files', 'generator.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'generator.cpp'])
    shutil.copy(generator, destination)
    if script != '':
        with open(os.path.join(*[problem_folder, 'src', 'script.sh']), 'w') as f:
            f.write(script)


def copy_checker(package_folder, problem_folder) -> None:
    """Copy checker from package to problem folder."""
    checker = os.path.join(*[package_folder, 'files', 'checker.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'checker.cpp'])
    shutil.copy(checker, destination)


def copy_testlib(package_folder, problem_folder) -> None:
    """Copy generator from package to problem folder."""
    testlib = os.path.join(*[package_folder, 'files', 'testlib.h'])
    destination = os.path.join(*[problem_folder, 'src', 'testlib.h'])
    shutil.copy(testlib, destination)


def copy_solutions(package_folder, problem_folder) -> None:
    """Copy solution files from package to problem folder."""
    solution_folder = os.path.join(package_folder, 'solutions')
    source_files = [os.path.join(solution_folder, x) for x in os.listdir(
        solution_folder) if not x.endswith('.desc')]
    destination = os.path.join(problem_folder, 'src')
    for f in source_files:
        shutil.copy(f, destination)


def check(package_folder, problem_folder):
    if not os.path.isdir(package_folder):
        print(package_folder, 'not a valid Polygon package folder')
        exit(1)
    if not os.path.isdir(problem_folder):
        print(problem_folder, 'is not a valid problem folder')
        exit(1)
    check_package(package_folder)
    check_problem(problem_folder)


def check_problem(problem_folder):
    pass


def check_package(package_folder):
    paths = ['files', 'solutions', 'problem.xml',
             'statement-sections', 'statements/english', 'tests', 'tags']
    paths = [os.path.join(package_folder, f) for f in paths]
    for path in paths:
        if not os.path.exists(path):
            print(os.path.basename(path), 'is not a valid path.')
            exit(1)


def write_statement(package_data, problem_folder):
    statement_dir = os.path.join(problem_folder, 'statement')
    with open(os.path.join(statement_dir, 'description.tex'), 'w') as f:
        print(package_data['statement'], file=f)
    with open(os.path.join(statement_dir, 'input.tex'), 'w') as f:
        print(package_data['input_description'], file=f)
    with open(os.path.join(statement_dir, 'output.tex'), 'w') as f:
        print(package_data['output_description'], file=f)
    with open(os.path.join(statement_dir, 'notes.tex'), 'w') as f:
        print(package_data['notes'], file=f)
    with open(os.path.join(statement_dir, 'tutorial.tex'), 'w') as f:
        print(package_data['tutorial'], file=f)


def get_package_data(package_folder):
    problem_data = {}
    problem_data['title'] = get_title(package_folder)
    problem_data['statement'] = get_statement(package_folder)
    problem_data['input_description'] = get_input_description(package_folder)
    problem_data['output_description'] = get_output_description(package_folder)
    problem_data['notes'] = get_notes(package_folder)
    problem_data['tutorial'] = get_tutorial(package_folder)
    return problem_data


def get_solution_tag(tag: str) -> str:
    if tag == 'main':
        return 'main-ac'
    elif tag == 'accepted':
        return 'alternative-ac'
    elif tag == 'wrong-answer':
        return 'wrong-answer'
    elif tag == 'memory-limit-exceeded':
        return 'memory-limit'
    elif tag.startswith('time-limit'):
        return 'time-limit'
    else:
        return 'runtime-error'


def get_scrips_xml(root) -> str:
    gen_scripts = ''
    for tests in root.findall('./judging/testset/tests/test'):
        script = tests.get('cmd')
        if script is not None:
            gen_scripts += script + '\n'
    return gen_scripts


def get_solutions_xml(root) -> dict:
    # TODO mnemonic names
    data = dict()
    for solutions in root.findall('./assets/solutions/solution'):
        solution_tag = solutions.get('tag')
        if solution_tag is None:
            continue
        tag = get_solution_tag(solution_tag)
        for filename in solutions.findall('source'):
            name = filename.get('path')
            if name is not None:
                data.setdefault(tag, []).append(os.path.basename(name))
    data['main-ac'] = ''.join(data['main-ac'])
    return data


def get_xml_data(package_folder):
    tree = ET.parse(os.path.join(package_folder, 'problem.xml'))
    root = tree.getroot()

    xml_data = {}
    xml_data['script'] = get_scrips_xml(root)
    xml_data['solutions'] = get_solutions_xml(root)
    return xml_data


def get_tags(problem_folder) -> dict:
    tags = {'en-us': list()}
    with open(os.path.join(problem_folder, 'tags'), 'r') as f:
        for line in f.readlines():
            tags['en-us'].append(line.rstrip())
    return tags


def update_problem_json(package_folder, problem_folder, tags, title, solutions):
    package_json = parse_json(os.path.join(
        *[package_folder, 'statements', 'english', 'problem-properties.json']))
    json_path = os.path.join(problem_folder, 'problem.json')
    problem_json = parse_json(json_path)

    problem_json['problem']['title'] = ''.join(title).rstrip()
    problem_json['problem']['time_limit'] = int(
        package_json['timeLimit'] / 1000)
    problem_json['problem']['memory_limit'] = int(
        (package_json['memoryLimit'] / 1024) / 1024)
    problem_json['problem']['interactive'] = False if not package_json['interaction'] else True
    problem_json['problem']['input_file'] = package_json['inputFile']
    problem_json['problem']['output_file'] = package_json['outputFile']
    problem_json['problem']['subject'] = tags
    problem_json['io_samples'] = len(package_json['sampleTests'])
    problem_json['solutions'] = solutions

    with open(json_path, 'w') as f:
        f.write(json.dumps(problem_json, ensure_ascii=False))


def convert(package_folder, problem_folder):
    check(package_folder, problem_folder)
    package_data = get_package_data(package_folder)
    xml_data = get_xml_data(package_folder)
    tags = get_tags(package_folder)
    write_statement(package_data, problem_folder)
    copy_input_files(package_folder, problem_folder)
    copy_output_files(package_folder, problem_folder)

    # Copiar todos de uma vez
    copy_testlib(package_folder, problem_folder)
    copy_solutions(package_folder, problem_folder)
    copy_checker(package_folder, problem_folder)
    copy_validator(package_folder, problem_folder)
    copy_generator(package_folder, problem_folder, xml_data['script'])
    update_problem_json(package_folder, problem_folder, tags,
                        package_data['title'], xml_data['solutions'])


def get_package_id(packages: dict) -> int:
    """Get the latest READY package ID from the dictionary."""
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


def convert_to_bytes(x) -> bytes:
    """Converts a string to bytes."""
    if isinstance(x, bytes):
        return x
    return bytes(str(x), 'utf8')


def get_apisig(method_name: str, secret: str, params: dict) -> bytes:
    """Generate 'apiSig' value for the API authorization."""
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    rand = convert_to_bytes(rand)

    param_list = [(convert_to_bytes(key), params[key]) for key in params]
    param_list.sort()

    apisig = rand + b'/' + convert_to_bytes(method_name) + b'?'
    apisig += b'&'.join([param[0] + b'=' + param[1] for param in param_list])
    apisig += b'#' + convert_to_bytes(secret)
    return rand + convert_to_bytes(hashlib.sha512(apisig).hexdigest())


def get_polygon_response(params, method, problem_id):
    tool_path = os.path.dirname(os.path.abspath(__file__))
    keys = parse_json(os.path.join(tool_path, 'secrets.json'))

    # Get list of all packages
    params['apiKey'] = keys['apikey']
    params['time'] = int(time.time())
    params['problemId'] = problem_id
    for key in params:
        params[key] = convert_to_bytes(params[key])
    params['apiSig'] = get_apisig(method, keys['secret'], params)

    url = 'https://polygon.codeforces.com/api/'
    response = requests.post(url + method, files=params)
    if response.status_code == 200:
        info_log(f'Request {method} successfull.')
    else:
        if response.status_code == 400:
            content = json.loads(response.content.decode())
            error_log("API status: " + content['status'])
            error_log(content['comment'])
            print(f"Wrong parameter of {method} method.")
        else:
            print("Could not connect to the API.")
        exit(1)
    return response.content


def download_package_polygon(package_folder):
    """Download zip package from Polygon."""
    problem_id = input('ID: ')

    content = json.loads(get_polygon_response(
        dict(), 'problem.packages', problem_id))

    # Get the correct package
    package_id = get_package_id(content['result'])

    # Get bytes of the package
    params = dict()
    params['packageId'] = package_id
    params['type'] = 'linux'
    response = get_polygon_response(params, 'problem.package', problem_id)

    # Save bytes as a zip file
    package = zipfile.ZipFile(io.BytesIO(response))
    package.extractall(package_folder)
    package.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package_folder')
    parser.add_argument('problem_folder')
    args = parser.parse_args()
    instance_paths(args.package_folder, args.problem_folder)
    download_package_polygon(args.package_folder)
    convert(args.package_folder, args.problem_folder)
