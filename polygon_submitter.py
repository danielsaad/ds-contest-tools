import sys
import time
import os
import random
import hashlib
import string
import requests
import time
from logger import info_log, error_log
from jsonutils import parse_json
from metadata import Paths
from utils import convert_to_bytes


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


def polygon_auth(method_name: str, params: dict) -> None:
    """Get response from Polygon API methods."""
    tool_path = os.path.dirname(os.path.abspath(__file__))
    keys = parse_json(os.path.join(tool_path, 'secrets.json'))

    params['apiKey'] = keys['polygon-apikey']
    params['time'] = int(time.time())
    with open(os.path.join(Paths.instance().dirs['problem_dir'], 'tmp_file.aux'), 'r') as f:
        params['problemId'] = f.readline()

    for key in params:
        params[key] = convert_to_bytes(params[key])
    params['apiSig'] = get_apisig(method_name, keys['polygon-secret'], params)

    info_log(f"Requesting {method_name}...")
    url = f"https://polygon.codeforces.com/api/{method_name}"
    response = requests.post(url, files=params)

    # TODO -> Print correct information about the return of 
    # the connection
    if (response.status_code != 200):
        if (response.status_code == 400):
            print(response.content)
        else:
            print(response.content)
        print("Could not connect to the API.")
        sys.exit(1)

    info_log(f"Request {method_name} successfully.")
    return response.content


def update_info(problem_json: dict):
    """Save general information of a problem."""
    interactive = problem_json['interactive']
    time_limit = problem_json['time_limit'] * 1000
    if (time_limit < 250 or time_limit > 15000):
        print("Time limit is only between 0.25s and 15s.")
        sys.exit(0)

    memory_limit = problem_json['memory_limit']
    if (memory_limit < 4 or memory_limit > 1024):
        print("Memory limit is only between 4MB and 1024MB.")
        sys.exit(0)

    params = dict(
        inputFile = problem_json['input_file'],
        outputFile = problem_json['output_file'],
        interactive = str(interactive).lower(),
        timeLimit = time_limit,
        memoryLimit = memory_limit)
    polygon_auth('problem.updateInfo', params)


def save_statement(interactive: bool, name: str):
    """Save statement information of a problem."""
    statement_dir = os.path.join(
        Paths.instance().dirs['problem_dir'], 'statement')

    lang = 'english'
    encoding = 'utf-8'
    statement_files = ['descricao.tex', 'entrada.tex', 'saida.tex','notas.tex','tutorial.tex']
    statement_files = [os.path.join(statement_dir, f) for f in statement_files]
    for file in statement_files:
        if (not os.path.exists(file)):
            print(f'File {os.path.basename(file)} does not exist.')
            sys.exit(0)

    with open(statement_files[0]) as f:
        legend = ''.join(f.readlines())
    with open(statement_files[1]) as f:
        inp = ''.join(f.readlines())
    with open(statement_files[2]) as f:
        out = ''.join(f.readlines())
    with open(statement_files[3]) as f:
        notes = ''.join(f.readlines())
    with open(statement_files[4]) as f:
        tutorial = ''.join(f.readlines())

    params = dict(
        lang = lang,
        encoding = encoding,
        name = name,
        legend = legend,
        input = inp,
        output = out,
        notes = notes,
        tutorial = tutorial)
    if (interactive):
        with open(os.path.join(statement_dir, 'interacao.tex')) as f:
            params['interactive'] = ''.join(f.readlines())

    polygon_auth('problem.saveStatement', params)


def save_statement_resources():
    """Save the statement resource files of a problem"""
    statement_dir = os.path.join(
        Paths.instance().dirs['problem_dir'], 'statement')
    for file in os.listdir(statement_dir):
        if (file.endswith('.tex')):
            continue

        with open(os.path.join(statement_dir, file), 'rb') as f:
            file_content = b''.join(f.readlines())

        params = dict()
        params['name'] = file
        params['file'] = file_content
        polygon_auth('problem.saveStatementResource', params)


def set_validator(name):
    """Set validator used by the problem."""
    params = dict()
    params['validator'] = name

    polygon_auth('problem.setValidator', params)


def set_checker(name):
    """Set checker used by the problem."""
    params = dict()
    params['checker'] = name

    polygon_auth('problem.setChecker', params)


def save_file(file_path: str, file_type: str):
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    params = dict()
    params['name'] = os.path.basename(file_path)
    params['file'] = file_content
    params['type'] = file_type
    # if (file_type == 'resource'):
    #     if (forTypes != '' and stages != '' and assets == ''):
    #         params['forTypes'] = forTypes
    #         params['stages'] = stages  # stages=COMPILE
    #         params['assets'] = assets  # assets=SOLUTION
    polygon_auth('problem.saveFile', params)


def save_solution(file_path, tag):
    """Save the solution file of a problem."""
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    if tag == 'main-ac':
        tag = 'MA'
    elif tag == 'alternative-ac':
        tag = 'OK'
    elif tag == 'wrong-anwser':
        tag = 'WA'
    elif tag == 'time-limit':
        tag = 'TL'
    else:
        tag = 'RE'

    params = dict()
    params['name'] = os.path.basename(file_path)
    params['file'] = file_content
    params['tag'] = tag
    polygon_auth('problem.saveSolution', params)


def save_files(solutions: dict):
    """Save source, resource and solution files of a problem."""
    src_dir = os.path.join(Paths.instance().dirs['problem_dir'], 'src')

    solution_files = []
    for key in solutions:
        if (isinstance(solutions[key], str)):
            solutions[key] = [f'{solutions[key]}']

        for s in solutions[key]:
            if (s == ''):
                continue
            solution_path = os.path.join(src_dir, s)
            if (not os.path.exists(solution_path)):
                print(f'Solution {s} does not exists.')
                sys.exit(0)
            save_solution(solution_path, key)
            solution_files.append(s)

    for file in os.listdir(src_dir):
        if file in solution_files:
            continue
        elif file.startswith('checker'):
            save_file(os.path.join(src_dir, file), 'source')
            set_checker(file)
        elif file.startswith('validator'):
            save_file(os.path.join(src_dir, file), 'source')
            set_validator(file)
        elif file.startswith('generator'):
            save_file(os.path.join(src_dir, file), 'source')
        else:
            save_file(os.path.join(src_dir, file), 'resource')


def save_tags(tag_list):
    """Save the tags of a problem."""
    tags = ''
    for tag in tag_list:
        tags += tag + ','
    tags[:-1]

    params = dict()
    params['tags'] = tags
    polygon_auth('problem.saveTags', params)


def save_test(tests_in_statement: int):
    """Save the inputs of a problem."""
    input_folder = os.path.join(Paths.instance().dirs['problem_dir'], 'input')
    if (not os.path.exists(input_folder)):
        print(f'Input folder does not exist.')
        sys.exit(0)
    tests_list = []
    for input_file in os.listdir(input_folder):
        testset = 'tests'  # Standard testset
        with open(os.path.join(input_folder, input_file), 'r') as f:
            test_input = ''.join(f.readlines())
        test_use_in_statements = (int(input_file) <= tests_in_statement)
        test_description = f'Test {input_file} converted from DS problem.'
        verify_input_output_for_statement = True
        check_existing = False

        params = dict()
        params['testset'] = testset
        params['testIndex'] = input_file
        params['testInput'] = test_input
        params['checkExisting'] = str(check_existing).lower()
        params['testDescription'] = test_description
        params['testUseInStatements'] = str(test_use_in_statements).lower()
        params['verifyInputOutputForStatements'] = str(
            verify_input_output_for_statement).lower()
        polygon_auth('problem.saveTest', params)


def send_to_polygon() -> None:
    """Make requests"""
    problem_dir = Paths.instance().dirs['problem_dir']
    tmp_file = os.path.join(problem_dir, 'tmp_file.aux')
    with open(tmp_file, 'w') as f:
        f.write(input("Problem ID: "))

    problem_json = parse_json(os.path.join(problem_dir, 'problem.json'))
    update_info(problem_json['problem'])
    save_statement(problem_json['problem']['interactive'], problem_json['problem']['title'])
    save_statement_resources()
    save_files(problem_json['solutions'])
    save_tags(problem_json['problem']['subject']['en_us'])
    save_test(problem_json['io_samples'])
    os.remove(tmp_file)
