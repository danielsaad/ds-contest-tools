import os
import sys
import time
import json
import random
import string
import hashlib
import requests
from metadata import Paths
from jsonutils import parse_json
from logger import info_log, error_log, debug_log
from fileutils import get_statement_files
from utils import convert_to_bytes, instance_paths, verify_problem_json, verify_path


LANGUAGE = 'english'
ENCONDING = 'utf-8'
TESTSET = 'tests'
VERIFY_IO_STATEMENT = True


def update_info(problem_metadata: dict) -> tuple:
    """Get general information parameters of the problem."""
    interactive = problem_metadata['interactive']
    time_limit = problem_metadata['time_limit'] * 1000
    if (time_limit < 250 or time_limit > 15000):
        print("Time limit is only between 0.25s and 15s.")
        sys.exit(0)
    memory_limit = problem_metadata['memory_limit_mb']
    if (memory_limit < 4 or memory_limit > 1024):
        print("Memory limit is only between 4MB and 1024MB.")
        sys.exit(0)

    params = {
        'inputFile': problem_metadata['input_file'],
        'outputFile': problem_metadata['output_file'],
        'interactive': str(interactive).lower(),
        'timeLimit': time_limit,
        'memoryLimit': memory_limit}
    return ('problem.updateInfo', params)


def save_statement(name: str, interactive: bool) -> tuple:
    """Get statement parameters of the problem."""
    if interactive:
        print("Polygon API does not receive interaction statement. "
              "Manual insertion will be needed.")

    statement_dir = os.path.join(
        Paths().get_problem_dir(), 'statement')

    statement_files = get_statement_files(statement_dir)
    with open(statement_files[0], 'r') as f:
        legend = ''.join(f.readlines())
    with open(statement_files[1], 'r') as f:
        inp = ''.join(f.readlines())
    with open(statement_files[2], 'r') as f:
        out = ''.join(f.readlines())
    with open(statement_files[3], 'r') as f:
        notes = ''.join(f.readlines())
    with open(statement_files[4], 'r') as f:
        tutorial = ''.join(f.readlines())

    params = {
        'lang': LANGUAGE,
        'encoding': ENCONDING,
        'name': name,
        'legend': legend,
        'input': inp,
        'output': out,
        'notes': notes,
        'tutorial': tutorial}
    return ('problem.saveStatement', params)


def save_statement_resources() -> list:
    """Get statement resource files of the problem, for example, images."""
    statement_dir = os.path.join(
        Paths().get_problem_dir(), 'statement')

    params_list = []
    for file in os.listdir(statement_dir):
        if file.endswith('.tex'):
            continue
        with open(os.path.join(statement_dir, file), 'rb') as f:
            file_content = b''.join(f.readlines())

        params = {
            'name': file,
            'file': file_content}
        params_list.append(('problem.saveStatementResource', params))
    return params_list


def save_script():
    """Verify if script exists and save it."""
    problem_folder = Paths().get_problem_dir()
    script_path = os.path.join(*[problem_folder, 'src', 'script.sh'])
    if not os.path.exists(script_path):
        return None

    with open(script_path, 'r') as f:
        scripts = f.readlines()
    params = {
        'testset': TESTSET,
        'source': ''.join(script.rstrip() + ' > $\n' for script in scripts)}

    return ('problem.saveScript', params)


def set_validator(name) -> tuple:
    """Set validator used by the problem."""
    params = {'validator': name}
    return ('problem.setValidator', params)


def set_checker(name) -> tuple:
    """Set checker used by the problem."""
    params = {'checker': name}
    return ('problem.setChecker', params)


def set_interactor(name) -> tuple:
    """Set interactor used by the problem."""
    params = {'interactor': name}
    return ('problem.setInteractor', params)


def save_file(file_path: str, file_type: str) -> tuple:
    """Get files of the problem."""
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'type': file_type}
    return ('problem.saveFile', params)


def save_solution(file_path: str, tag: str) -> tuple:
    """Get solution files of the problem."""
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    if tag == 'main-ac':
        tag = 'MA'
    elif tag == 'alternative-ac':
        tag = 'OK'
    elif tag == 'wrong-answer':
        tag = 'WA'
    elif tag == 'time-limit':
        tag = 'TL'
    elif tag == 'time-limit-or-ac':
        tag = 'TO'
    elif tag == 'time-limit-or-memory-limit':
        tag = 'TM'
    elif tag == 'memory-limit':
        tag = 'ML'
    elif tag == 'presentation-error':
        tag = 'PE'
    else:
        tag = 'RE'

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'tag': tag}
    return ('problem.saveSolution', params)


def save_files(solutions: dict) -> list:
    """Save auxiliar, source and solution files of a problem."""
    src_dir = os.path.join(Paths().get_problem_dir(), 'src')

    # Save solution files and store them in a list
    params_list = []
    solution_files = []
    for key in solutions:
        if key == 'main-ac':
            solutions[key] = list(solutions[key].split(' '))

        for s in solutions[key]:
            if (s == ''):
                continue
            solution_path = os.path.join(src_dir, s)
            verify_path(solution_path)
            params_list.append(save_solution(solution_path, key))
            solution_files.append(s)

    # Save resource, source and aux files
    setters = []
    for file in os.listdir(src_dir):
        if file == 'testlib.h':
            continue
        if file in solution_files or file.endswith('.sh'):
            continue
        if file.endswith('.h'):
            params_list.append(
                save_file(os.path.join(src_dir, file), 'resource'))
            continue

        params_list.append(save_file(os.path.join(src_dir, file), 'source'))
        if file.startswith('checker'):
            setters.append(set_checker(file))
        elif file.startswith('validator'):
            setters.append(set_validator(file))
        elif file.startswith('interactor'):
            setters.append(set_interactor(file))

    return params_list + setters


def save_tags(tag_list: list) -> tuple:
    """Get tags parameters of the problem."""
    tags = ','.join(tag_list)
    params = {'tags': tags}
    return ('problem.saveTags', params)


def save_test(tests_in_statement: int, interactive: bool) -> tuple:
    """Get input files of the problem."""
    problem_folder = Paths().get_problem_dir()
    input_folder = os.path.join(problem_folder, 'input')
    output_folder = os.path.join(problem_folder, 'output')
    verify_path(input_folder)

    input_files = [f for f in os.listdir(input_folder)
                   if not f.endswith('.interactive')]
    total_inputs = len(input_files)

    script_path = os.path.join(*[problem_folder, 'src', 'script.sh'])
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            total_scripts = len(f.readlines())
        total_inputs -= total_scripts

    if interactive:
        total_inputs += tests_in_statement

    params_list = []
    script_written = False
    for input_file in os.listdir(input_folder):
        if input_file.endswith('.interactive'):
            continue
        if int(input_file) > total_inputs:
            continue

        test_use_in_statements = (int(input_file) <= tests_in_statement)
        test_description = f'Test {input_file} from DS contest tools.'
        input_path = os.path.join(input_folder, input_file)
        with open(input_path, 'r') as f:
            test_input = f.read()

        params = {
            'testset': TESTSET,
            'testIndex': input_file,
            'testInput': test_input,
            'checkExisting': 'false',
            'testDescription': test_description,
            'testUseInStatements': str(test_use_in_statements).lower()}

        if interactive and test_use_in_statements:
            if not script_written:
                # Generate script to save .interactive info
                script = save_script()
                if script is not None:
                    params_list.append(script)
                script_written = True

            input_path += '.interactive'
            verify_path(input_folder)

            output_path = os.path.join(
                output_folder, input_file + '.interactive')
            verify_path(output_folder)

            with open(input_path, 'r') as f:
                test_input_statement = f.read()
            with open(output_path, 'r') as f:
                test_output_statement = f.read()

            params['testInputForStatements'] = test_input_statement
            params['testOutputForStatements'] = test_output_statement
            params.pop('testInput')

        params_list.append(('problem.saveTest', params))
    return (params_list, script_written)


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


def add_auth_parameters(method: str, params: dict, problem_id: str, keys: dict) -> dict:
    """Add authentication parameters to the Polygon request."""
    params['apiKey'] = keys["apikey"]
    params['time'] = int(time.time())
    params['problemId'] = problem_id
    for key in params:
        params[key] = convert_to_bytes(params[key])
    params['apiSig'] = get_apisig(method, keys["secret"], params)
    return params


def get_requests_list() -> list:
    """Get each request needed to convert the problem to Polygon."""
    path_json = os.path.join(
        Paths().get_problem_dir(), 'problem.json')
    problem_metadata = parse_json(path_json)
    verify_problem_json(problem_metadata)

    requests_list = []
    interactive = problem_metadata['problem']['interactive']
    requests_list.append(update_info(problem_metadata['problem']))
    requests_list.append(save_statement(
        problem_metadata['problem']['title'], interactive))
    requests_list.append(
        save_tags(problem_metadata['problem']['subject']['en_us']))
    requests_list = requests_list + save_statement_resources()
    requests_list = requests_list + save_files(problem_metadata['solutions'])
    test_results = save_test(problem_metadata['io_samples'], interactive)
    requests_list = requests_list + test_results[0]
    script = save_script()
    if not test_results[1] and script is not None:
        requests_list.append(script)
    return requests_list


def add_requests_info(requests_list) -> list:
    """Add authentication parameters to the Polygon request."""
    tool_path = os.path.dirname(os.path.abspath(__file__))
    keys = parse_json(os.path.join(tool_path, 'secrets.json'))

    problem_id = input('ID: ')
    for method, params in requests_list:
        params = add_auth_parameters(method, params, problem_id, keys)
    return requests_list


def verify_response(response, method, params) -> None:
    """Verify if the request from Polygon was successfull."""
    if response.status_code == 200:
        info_log(f'Request {method} successfull.')
    else:
        if response.status_code == 400:
            content = json.loads(response.content.decode())
            parameters = 'Parameters:\n'
            for key, value in params.items():
                parameters += f"{key}: {value}\n"

            error_log("API status: " + content['status'])
            error_log(content['comment'] + 
                      '\nCheck debug.log for parameters information')
            debug_log("API status: " + content['status'])
            debug_log(parameters)
            print(f"Wrong parameter of {method} method.")
        else:
            print("Could not connect to the API.")
        sys.exit(1)


def send_to_polygon(problem_folder) -> None:
    """Send problem to Polygon."""
    verify_path(problem_folder)
    instance_paths(problem_folder)

    # Get list of requests to Polygon
    requests_list = get_requests_list()
    requests_list = add_requests_info(requests_list)

    # Make persistent connection with Polygon and send all requests
    conn = requests.Session()
    url = 'https://polygon.codeforces.com/api/'
    for method, params in requests_list:
        response = conn.post(url + method, files=params)
        verify_response(response, method, params)
