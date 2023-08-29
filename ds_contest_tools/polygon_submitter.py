import os
from typing import Dict, List, Tuple, Union

from .fileutils import get_statement_files
from .jsonutils import parse_json
from .logger import error_log, warning_log
from .metadata import Paths
from .polygon_connection import (check_polygon_id, submit_concurrent_testcases,
                                 submit_requests_list)
from .toolchain import generate_inputs
from .utils import check_problem_metadata, verify_path

LANGUAGE = 'english'
ENCODING = 'utf-8'
TESTSET = 'tests'
VERIFY_IO_STATEMENT = True
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'bmp', 'ico'}


def update_info(problem_metadata: dict) -> tuple:
    """Get general information parameters of the problem.

    Args:
        problem_metadata: A dictionary containing metadata about the problem.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    interactive: bool = problem_metadata['interactive']
    time_limit: int = problem_metadata['time_limit'] * 1000
    memory_limit: int = problem_metadata['memory_limit_mb']

    if not 250 <= time_limit <= 15000:
        error_log("Time limit is only between 0.25s and 15s.")

    if not 4 <= memory_limit <= 1024:
        error_log("Memory limit is only between 4MB and 1024MB.")

    params: dict = {
        'inputFile': problem_metadata['input_file'],
        'outputFile': problem_metadata['output_file'],
        'interactive': str(interactive).lower(),
        'timeLimit': time_limit,
        'memoryLimit': memory_limit
    }
    return ('problem.updateInfo', params)


def save_statement(name: str, interactive: bool) -> tuple:
    """Get statement parameters of the problem.

    Args:
        name: The name of the statement file.
        interactive: Whether the statement is interactive or not.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    if interactive:
        warning_log("Polygon API does not receive interaction statement. "
                 "Manual insertion will be needed.")

    statement_dir: str = os.path.join(
        Paths().get_problem_dir(), 'statement')

    statement_files: List[str] = get_statement_files(statement_dir)
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

    params: dict = {
        'lang': LANGUAGE,
        'encoding': ENCODING,
        'name': name,
        'legend': legend,
        'input': inp,
        'output': out,
        'notes': notes,
        'tutorial': tutorial}
    return ('problem.saveStatement', params)


def save_statement_resources() -> List[Tuple[str, dict]]:
    """Get statement resource files of the problem, e.g, images or PDFs.

    Returns:
        A list of tuples, where each tuple contains the method and the 
        parameters for the request.
    """
    problem_dir: str = os.path.join(Paths().get_problem_dir())

    parameters_list = []
    for file_name in os.listdir(problem_dir):
        filepath = os.path.join(problem_dir, file_name)
        if os.path.isdir(filepath):
            continue
        _, extension = os.path.splitext(file_name)
        if extension.lower()[1:] not in IMAGE_EXTENSIONS:
            continue
        with open(filepath, 'rb') as file:
            file_content = file.read()
        params = {
            'name': file_name,
            'file': file_content
        }
        parameters_list.append(('problem.saveStatementResource', params))
    return parameters_list


def save_testcases(tests_in_statement: int, interactive: bool, tmp_folder: str) -> List[Tuple[str, dict]]:
    """Get list of requests to save the script and the statement testcases of the problem.

    Args:
        tests_in_statement: Number of tests to be used as example in the statement.
        interactive: Whether the problem is interactive or not.
        tmp_folder: Path to the temporary folder.

    Returns:
        A list of tuples, where each tuple contains the method and the parameters for the request.
    """
    script_requests: tuple = save_script(tmp_folder)

    statement_tests: list = define_statement_tests(tests_in_statement, interactive)

    requests_for_polygon: list = []
    requests_for_polygon += script_requests
    requests_for_polygon += statement_tests
    return requests_for_polygon


def save_script(tmp_folder: str) -> List[Tuple[str, dict]]:
    """Verify if script exists and save it.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    problem_folder: str = Paths().get_problem_dir()
    script_path: str = os.path.join(problem_folder, 'src', 'script.sh')

    # Read scripts
    with open(script_path, 'r') as f:
        scripts: list = f.readlines()
    if len(scripts) == 0:
        return []

    # Get number of testcases per generator
    gen_index_path = os.path.join(os.path.dirname(tmp_folder), 'index_gen')
    verify_path(gen_index_path)
    with open(gen_index_path, 'r') as f:
        gen_index: list = f.readlines()

    # Generate script for Polygon
    index: int = 1
    source: str = ''
    for i in range(min(len(scripts), len(gen_index))):
        if int(gen_index[i]) == 0:
            # Unique generator
            testcases = str(index)
            index += 1
        else: 
            # Multigenerator
            testcases = '{' + f'{index}-{index + int(gen_index[i]) - 1}' + '}'
            index += int(gen_index[i])

        source += f'{scripts[i].rstrip()} > {testcases}\n'

    params = {
        'testset': TESTSET,
        'source': source
    }

    return [('problem.saveScript', params)]


def set_validator(name: str) -> Tuple[str, dict]:
    """Set validator used by the problem.

    Args:
        name: Name of the validator used by the problem.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    params: dict = {'validator': name}
    return ('problem.setValidator', params)


def set_checker(name: str) -> Tuple[str, dict]:
    """Set checker used by the problem.

    Args:
        name: Name of the checker used by the problem.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    params: dict = {'checker': name}
    return ('problem.setChecker', params)


def set_interactor(name: str) -> Tuple[str, dict]:
    """Set interactor used by the problem.

    Args:
        name: Name of the interactor used by the problem

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    params: dict = {'interactor': name}
    return ('problem.setInteractor', params)


def save_file(file_path: str, file_type: str, grader: bool = False) -> tuple:
    """Get parameters of the files used to compile the problem.

    Args:
        file_path: Path to the file to be saved.
        file_type: Type of the file, e.g., 'source', 'resource', 'aux'.
        grader: A boolean indicating whether the problem has a grader.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    with open(file_path, 'rb') as f:
        file_content = f.read()

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'type': file_type
    }

    if grader:
        params['forTypes'] = "cpp.*" if file_path.endswith(('.cpp', '.h')) else "python.*"
        params['main'] = "false"
        params['stages'] = "COMPILE"
        params['assets'] = "SOLUTION"

    return ('problem.saveFile', params)


def save_solution(file_path: str, tag: str) -> Tuple[str, dict]:
    """Get solution files of the problem.

    Args:
        file_path: Path to the solution file.
        tag: Tag of the type of the problem.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    with open(file_path, 'rb') as f:
        file_content = f.read()

    solution_tags: dict = {
        'main-ac': 'MA',
        'alternative-ac': 'OK',
        'wrong-answer': 'WA',
        'time-limit': 'TL',
        'time-limit-or-ac': 'TO',
        'time-limit-or-memory-limit': 'TM',
        'memory-limit': 'ML',
        'presentation-error': 'PE',
        'runtime-error': 'RE'
    }

    tag = solution_tags.get(tag)
    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'tag': tag
    }

    return ('problem.saveSolution', params)


def save_files(solutions: dict, interactive: bool, grader: bool) -> List[Dict[str, dict]]:
    """Save auxiliary, source and solution files of a problem.

    Args:
        solutions: Dictionary containing the solutions of the problem.
        interactive: A boolean indicating whether the problem is interactive.
        grader: A boolean indicating whether the problem has a grader.

    Returns:
        A list of tuples, where each tuple contains the method and the 
        parameters for the request.
    """
    source_dir: str = os.path.join(Paths().get_problem_dir(), 'src')
    verify_path(source_dir)
    
    # Save solutions parameters
    solutions_saved = set()
    solutions_parameters: list = []
    for key, solution_list in solutions.items():
        if key == 'main-ac':
            solution_list = [solution_list]

        for solution in solution_list:
            # Skip if solution is an empty string
            if not solution:
                continue
            solution_path: str = os.path.join(source_dir, solution)
            verify_path(solution_path)
            solutions_parameters.append(save_solution(solution_path, key))
            solutions_saved.add(solution)

    # Save source, resource and auxiliary files
    ignored_files: set = {'testlib.h', 'script.sh'}
    grader_files: set = {'grader.cpp', 'main.py'}
    files_parameters: list = []
    for file in os.listdir(source_dir):
        if file in solutions_saved or file in ignored_files or not os.path.isfile(os.path.join(source_dir, file)):
            continue

        file_path: str = os.path.join(source_dir, file)
        verify_path(file_path)

        if grader and file in grader_files:
            # Save grader files
            files_parameters.append(save_file(file_path, 'resource', grader))
        elif file.endswith('.h'):
            # Save resource files
            files_parameters = [save_file(file_path, 'resource', grader)] + files_parameters
        elif file.endswith(('.aux', '.sh')):
            # Save auxiliary files
            files_parameters.append(save_file(file_path, 'aux'))
        elif file == 'interactor.cpp' and not interactive:
            continue
        else:
            # Save source files
            files_parameters.append(save_file(file_path, 'source'))
            if file == 'checker.cpp':
                files_parameters.append(set_checker(file))
            elif file == 'validator.cpp':
                files_parameters.append(set_validator(file))
            elif file == 'interactor.cpp':
                files_parameters.append(set_interactor(file))

    return files_parameters + solutions_parameters


def save_tags(tag_list: List[str]) -> Tuple[str, dict]:
    """Get tags parameters of the problem.

    Args:
        tag_list: A list of strings containing the tags for the problem.

    Returns:
        A tuple containing the method and parameters for the request.
    """
    tags: str = ','.join(tag_list)
    params: dict = {'tags': tags}
    return ('problem.saveTags', params)


def define_statement_tests(tests_in_statement: int, interactive: bool) -> List[Tuple[list, bool]]:
    """Generate a list of requests to update the test in statement.

    Args:
        tests_in_statement: Number of tests to show in the statement
        interactive: A boolean indicating whether the problem is interactive.

    Returns:
        A list of tuples which contain the method and parameters for the request.
    """
    problem_folder: str = Paths().get_problem_dir()
    input_folder: str = os.path.join(problem_folder, 'input')
    output_folder: str = os.path.join(problem_folder, 'output')
    verify_path(input_folder)
    verify_path(output_folder)

    total_inputs: int = len(os.listdir(input_folder))
    parameters_list: list = []
    for input_file in range(1, tests_in_statement + 1):
        # Index has leading zeros in order to sort them for requests
        input_file = str(input_file)
        params: dict = {
            'testset': TESTSET,
            'testIndex': input_file.zfill(len(str(total_inputs))),
            'checkExisting': 'false',
            'testUseInStatements': 'true',
        }

        if interactive:
            input_path = os.path.join(
                input_folder, input_file + '.interactive')
            output_path = os.path.join(
                output_folder, input_file + '.interactive')
            verify_path(input_path)
            verify_path(output_path)

            with open(input_path, 'r') as f:
                test_input_statement = f.read()
            with open(output_path, 'r') as f:
                test_output_statement = f.read()

            params['testInputForStatements'] = test_input_statement
            params['testOutputForStatements'] = test_output_statement

        parameters_list.append(('problem.saveTest', params))
    return parameters_list


def save_manual_testcases(problem_id: str, io_samples: int) -> None:
    """Send testcases manually to Polygon.

    Args:
        problem_id: ID of the Polygon problem.
        io_samples: Number of examples testcases.
    """
    problem_folder: str = Paths().get_problem_dir()
    input_folder: str = os.path.join(problem_folder, 'input')
    output_folder: str = os.path.join(problem_folder, 'output')
    verify_path(input_folder)
    verify_path(output_folder)

    parameters: list = []
    testcases: int = len([f for f in os.listdir(input_folder) if not f.endswith('.interactive')])
    for input_file in range(testcases):
        input_file = str(input_file + 1)
        test_description: str = f'Manual test {input_file} from DS contest tools.'
        input_path = os.path.join(input_folder, input_file)
        with open(input_path, 'r') as f:
            test_input = f.read()
        params: dict = {
            'testset': TESTSET,
            'testIndex': input_file.zfill(len(str(testcases))),
            'testInput': test_input,
            'checkExisting': 'false',
            'testDescription': test_description,
            'testUseInStatements': 'false' if int(input_file) > io_samples else 'true'
        }
        parameters.append(params)
    parameters = sorted(parameters, key=lambda x: x['testIndex'])
    submit_concurrent_testcases(problem_id, parameters)


def get_requests_list(problem_id: str, manual_testcases: bool) -> List[Tuple[str, dict]]:
    """Get each request needed to convert the problem to Polygon.

    Args:
        manual_testcases: A boolean indicating whether to send testcases manually to Polygon.

    Returns:
        A list of tuples, where each tuple contains the method and the 
        parameters for the request.
    """
    path_json = os.path.join(Paths().get_problem_dir(), 'problem.json')
    problem_metadata = parse_json(path_json)
    check_problem_metadata(problem_metadata)

    tmp_folder = os.path.join(Paths().get_tmp_output_dir(), 'scripts')
    generate_inputs(move=False, output_folder=tmp_folder)

    requests_list = []

    # Get general information parameters of the problem
    requests_list.append(update_info(problem_metadata['problem']))

    # Get statement parameters of the problem
    interactive = problem_metadata['problem']['interactive']
    requests_list.append(save_statement(
        problem_metadata['problem']['title'], interactive))

    # Get tags parameters of the problem
    tags = problem_metadata['problem']['subject']['en_us']
    requests_list.append(save_tags(tags))

    # Get statement resources parameters of the problem
    requests_list += save_statement_resources()

    # Get source and solution files of the problem
    grader = problem_metadata['problem']['grader']
    requests_list += save_files(problem_metadata['solutions'], interactive, grader)

    # Get test parameters of the problem
    if manual_testcases:
        save_manual_testcases(problem_id, problem_metadata['io_samples'])
    else:
        requests_list += save_testcases(
            problem_metadata['io_samples'], interactive, tmp_folder)

    return requests_list


def send_to_polygon(problem_id: Union[str, None], manual_testcases: bool = False) -> None:
    """Send problem to Polygon.

    Args:
        problem_id: ID of the Polygon problem.
        manual_testcases: A boolean indicating whether to send testcases manually to Polygon.
    """
    problem_id: str = check_polygon_id(problem_id)
    requests_list: List[Tuple[str, dict]] = get_requests_list(problem_id, manual_testcases)
    submit_requests_list(requests_list, problem_id)
