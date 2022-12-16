import sys
import time
import os
import random
import hashlib
import string
import requests
import time
import json
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


def update_info(problem_json: dict) -> tuple[str, dict]:
    """Get general information parameters of the problem."""
    interactive = problem_json['interactive']
    time_limit = problem_json['time_limit'] * 1000
    if (time_limit < 250 or time_limit > 15000):
        print("Time limit is only between 0.25s and 15s.")
        sys.exit(0)
    memory_limit = problem_json['memory_limit']
    if (memory_limit < 4 or memory_limit > 1024):
        print("Memory limit is only between 4MB and 1024MB.")
        sys.exit(0)

    params = {
        'inputFile': problem_json['input_file'],
        'outputFile': problem_json['output_file'],
        'interactive': str(interactive).lower(),
        'timeLimit': time_limit,
        'memoryLimit': memory_limit}
    return ('problem.updateInfo', params)


def save_statement(name: str) -> tuple[str, dict]:
    """Get statement parameters of the problem."""
    statement_dir = os.path.join(
        Paths.instance().dirs['problem_dir'], 'statement')

    statement_files = ['description.tex', 'input.tex',
                       'output.tex', 'notes.tex', 'tutorial.tex']
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

    params = {
        'lang': 'english',
        'encoding': 'utf-8',
        'name': name,
        'legend': legend,
        'input': inp,
        'output': out,
        'notes': notes,
        'tutorial': tutorial}
    return ('problem.saveStatement', params)


def save_statement_resources() -> list:
    """Get statement resource files of the problem."""
    statement_dir = os.path.join(
        Paths.instance().dirs['problem_dir'], 'statement')

    params_list = []
    for file in os.listdir(statement_dir):
        if (file.endswith('.tex')):
            continue
        with open(os.path.join(statement_dir, file), 'rb') as f:
            file_content = b''.join(f.readlines())

        params = {
            'name': file,
            'file': file_content}
        params_list.append(('problem.saveStatementResource', params))
    return params_list


def set_validator(name) -> tuple[str, dict]:
    """Set validator used by the problem."""
    params = {'validator': name}
    return ('problem.setValidator', params)


def set_checker(name) -> tuple[str, dict]:
    """Set checker used by the problem."""
    params = {'checker': name}
    return ('problem.setChecker', params)


def set_interactor(name) -> tuple[str, dict]:
    """Set interactor used by the problem."""
    params = {'interactor': name}
    return ('problem.setInteractor', params)


def save_file(file_path: str, file_type: str) -> tuple[str, dict]:
    """Get files of the problem."""
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'type': file_type}
    return ('problem.saveFile', params)


def save_solution(file_path: str, tag: str) -> tuple[str, dict]:
    """Get solution files of the problem."""
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

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'tag': tag}
    return ('problem.saveSolution', params)


def save_files(solutions: dict) -> list:
    """Save auxiliar, source and solution files of a problem."""
    src_dir = os.path.join(Paths.instance().dirs['problem_dir'], 'src')

    params_list = []
    solution_files = []
    for key in solutions:
        if key == 'main-ac':
            solutions[key] = list(solutions[key].split(' '))

        for s in solutions[key]:
            if (s == ''):
                continue
            solution_path = os.path.join(src_dir, s)
            if (not os.path.exists(solution_path)):
                print(f'Solution file {s} does not exist.')
                sys.exit(0)
            params_list.append(save_solution(solution_path, key))
            solution_files.append(s)

    setters = []
    for file in os.listdir(src_dir):
        if file in solution_files:
            continue
        elif file.startswith('checker'):
            params_list.append(
                save_file(os.path.join(src_dir, file), 'source'))
            setters.append(set_checker(file))
        elif file.startswith('validator'):
            params_list.append(
                save_file(os.path.join(src_dir, file), 'source'))
            setters.append(set_validator(file))
        elif file.startswith('interactor'):
            params_list.append(
                save_file(os.path.join(src_dir, file), 'source'))
            setters.append(set_interactor(file))
        elif file.startswith('generator'):
            params_list.append(
                save_file(os.path.join(src_dir, file), 'source'))
        else:
            params_list.append(save_file(os.path.join(src_dir, file), 'aux'))
    return params_list + setters


def save_tags(tag_list: list) -> tuple[str, dict]:
    """Get tags parameters of the problem."""
    tags = ','.join(tag_list)
    params = {'tags': tags}
    return ('problem.saveTags', params)


def save_test(tests_in_statement: int) -> list:
    """Get input files of the problem."""
    input_folder = os.path.join(Paths.instance().dirs['problem_dir'], 'input')
    if (not os.path.exists(input_folder)):
        print(f'Input folder does not exist.')
        sys.exit(0)

    params_list = []
    for input_file in os.listdir(input_folder):
        testset = 'tests'
        with open(os.path.join(input_folder, input_file), 'r') as f:
            test_input = ''.join(f.readlines())
        test_use_in_statements = (int(input_file) <= tests_in_statement)
        test_description = f'Test {input_file} from DS contest tools.'
        verify_input_output_for_statement = True
        check_existing = False

        params = {
            'testset': testset,
            'testIndex': input_file,
            'testInput': test_input,
            'checkExisting': str(check_existing).lower(),
            'testDescription': test_description,
            'testUseInStatements': str(test_use_in_statements).lower(),
            'verifyInputOutputForStatements': str(
                verify_input_output_for_statement).lower()}
        params_list.append(('problem.saveTest', params))
    return params_list


def get_requests_list() -> list[tuple]:
    problem_dir = Paths.instance().dirs['problem_dir']
    problem_json = parse_json(os.path.join(problem_dir, 'problem.json'))

    requests_list = []
    requests_list.append(update_info(problem_json['problem']))
    requests_list.append(save_statement(problem_json['problem']['title']))
    requests_list.append(
        save_tags(problem_json['problem']['subject']['en_us']))
    if (problem_json['problem']['interactive']):
        requests_list.append(set_interactor('interactor.cpp'))
    requests_list = requests_list + save_statement_resources()
    requests_list = requests_list + save_files(problem_json['solutions'])
    requests_list = requests_list + save_test(problem_json['io_samples'])
    return requests_list


def send_to_polygon() -> None:
    """Send problem information to Polygon."""
    problem_id = input('ID: ')
    requests_list = get_requests_list()
    tool_path = os.path.dirname(os.path.abspath(__file__))
    keys = parse_json(os.path.join(tool_path, 'secrets.json'))

    for method, params in requests_list:
        params['apiKey'] = keys["apikey"]
        params['time'] = int(time.time())
        params['problemId'] = problem_id

        for key in params:
            params[key] = convert_to_bytes(params[key])
        params['apiSig'] = get_apisig(method, keys["secret"], params)

    conn = requests.Session()
    url = 'https://polygon.codeforces.com/api/'
    for method, params in requests_list:
        response = conn.post(url + method, files=params)
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
            sys.exit(1)
