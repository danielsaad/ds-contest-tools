import os
import sys
from typing import Dict, List, Tuple, Union

from fileutils import get_statement_files
from jsonutils import parse_json
from logger import error_log, info_log
from metadata import Paths
from polygon_connection import check_polygon_id, submit_requests_list
from utils import check_problem_metadata, instance_paths, verify_path

LANGUAGE = 'english'
ENCODING = 'utf-8'
TESTSET = 'tests'
VERIFY_IO_STATEMENT = True


def update_info(problem_metadata: dict) -> tuple:
    """
    Get general information parameters of the problem.

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
        sys.exit(0)

    if not 4 <= memory_limit <= 1024:
        error_log("Memory limit is only between 4MB and 1024MB.")
        sys.exit(0)

    params: dict = {
        'inputFile': problem_metadata['input_file'],
        'outputFile': problem_metadata['output_file'],
        'interactive': str(interactive).lower(),
        'timeLimit': time_limit,
        'memoryLimit': memory_limit
    }
    return ('problem.updateInfo', params)


def save_statement(name: str, interactive: bool) -> tuple:
    """
    Get statement parameters of the problem.

    Args:
        name: The name of the statement file.
        interactive: Whether the statement is interactive or not.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    if interactive:
        info_log("Polygon API does not receive interaction statement. "
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
    """
    Get statement resource files of the problem, e.g, images or PDFs.

    Returns:
        A list of tuples, where each tuple contains the method and the 
        parameters for the request.
    """
    statement_dir: str = os.path.join(
        Paths().get_problem_dir(), 'statement')

    parameters_list = []
    for file in os.listdir(statement_dir):
        if file.endswith('.tex'):
            continue
        with open(os.path.join(statement_dir, file), 'rb') as f:
            file_content = b''.join(f.readlines())
        params = {
            'name': file,
            'file': file_content
        }
        parameters_list.append(('problem.saveStatementResource', params))
    return parameters_list


def save_script() -> Tuple[str, dict]:
    """
    Verify if script exists and save it.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    problem_folder: str = Paths().get_problem_dir()
    script_path: str = os.path.join(problem_folder, 'src', 'script.sh')
    if not os.path.exists(script_path):
        return None

    with open(script_path, 'r') as f:
        scripts = f.readlines()

    source: str = ''.join(script.rstrip() + ' > $\n' for script in scripts)
    params = {
        'testset': TESTSET,
        'source': source
    }

    return ('problem.saveScript', params)


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


def save_file(file_path: str, file_type: str) -> tuple:
    """Get parameters of the files used to compile the problem.

    Args:
        file_path: Path to the file to be saved.
        file_type: Type of the file, e.g., 'source', 'resource', 'aux'.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

    params = {
        'name': os.path.basename(file_path),
        'file': file_content,
        'type': file_type
    }
    return ('problem.saveFile', params)


def save_solution(file_path: str, tag: str) -> Tuple[str, dict]:
    """Get solution files of the problem.

    Args:
        file_path: Path to the solution file.
        tag: Tag of the type of the problem.

    Returns:
        A tuple containing the method and the parameters for the request.
    """
    with open(file_path, 'r') as f:
        file_content = ''.join(f.readlines())

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


def save_files(solutions: dict) -> List[Dict[str, dict]]:
    """Save auxiliar, source and solution files of a problem.

    Args:
        solutions: Dictionary containing the solutions of the problem.

    Returns:
        list: _description_
    """
    src_dir: str = os.path.join(Paths().get_problem_dir(), 'src')
    parameters_list: list = []
    solution_files: set = set()
    for key in solutions:
        if key == 'main-ac':
            solutions[key] = list(solutions[key].split(' '))

        for solution in solutions[key]:
            if not solution:
                continue
            solution_path: str = os.path.join(src_dir, solution)
            verify_path(solution_path)
            parameters_list.append(save_solution(solution_path, key))
            solution_files.add(solution)

    # Save resource, source and aux files
    setters: list = []
    for file in os.listdir(src_dir):
        if file in solution_files or file.endswith('.sh') or file == 'testlib.h':
            continue
        file_path: str = os.path.join(src_dir, file)
        verify_path(file_path)

        # Save resource files
        if file.endswith('.h'):
            parameters_list.append(
                save_file(file_path, 'resource'))
            continue

        # Save source files
        parameters_list.append(save_file(file_path, 'source'))
        if file.startswith('checker'):
            setters.append(set_checker(file))
        elif file.startswith('validator'):
            setters.append(set_validator(file))
        elif file.startswith('interactor'):
            setters.append(set_interactor(file))

    return parameters_list + setters


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


def save_test(tests_in_statement: int, interactive: bool) -> list:
    """
    Generate a list of requests to save input and output files for a problem.

    Args:
        tests_in_statement: The number of tests shown to the user.
        interactive: A boolean indicating whether the problem is interactive.

    Returns:
        A tuple containing a list of requests to save the test input and output files
        as well as any interactive input/output files if applicable, and a boolean indicating
        whether a script was written to save the interactive input/output files.
    """
    problem_folder: str = Paths().get_problem_dir()
    input_folder: str = os.path.join(problem_folder, 'input')
    output_folder: str = os.path.join(problem_folder, 'output')
    verify_path(input_folder)
    verify_path(output_folder)

    # Get quantity of valid tests to send to Polygon
    total_inputs: int = len([f for f in os.listdir(input_folder)
                             if not f.endswith('.interactive')])
    total_inputs += tests_in_statement if interactive else 0
    script_path: str = os.path.join(problem_folder, 'src', 'script.sh')
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            total_scripts = len(f.readlines())
            total_inputs -= total_scripts

    parameters_list: list = []
    for input_file in os.listdir(input_folder):
        if input_file.endswith('.interactive'):
            continue
        if int(input_file) > total_inputs:
            continue

        test_use_in_statements: int = (int(input_file) <= tests_in_statement)
        test_description: str = f'Test {input_file} from DS contest tools.'
        input_path: str = os.path.join(input_folder, input_file)
        with open(input_path, 'r') as f:
            test_input = f.read()

        params: dict = {
            'testset': TESTSET,
            'testIndex': input_file,
            'testInput': test_input,
            'checkExisting': 'false',
            'testDescription': test_description,
            'testUseInStatements': str(test_use_in_statements).lower()
        }

        # Save interactive test and its unique input/output statement
        if interactive and test_use_in_statements:
            input_path += '.interactive'
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


def get_requests_list() -> List[Tuple[str, dict]]:
    """Get each request needed to convert the problem to Polygon.

    Returns:
        A list of tuples, where each tuple contains the method and the 
        parameters for the request.
    """
    path_json = os.path.join(Paths().get_problem_dir(), 'problem.json')
    problem_metadata = parse_json(path_json)
    check_problem_metadata(problem_metadata)

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
    requests_list += save_files(problem_metadata['solutions'])

    # Get test parameters of the problem
    requests_list += save_test(problem_metadata['io_samples'], interactive)

    # Get script parameters of the problem
    if script := save_script():
        if script is not None:
            requests_list.append(script)

    return requests_list


def send_to_polygon(problem_folder: str, problem_id: Union[str, None]) -> None:
    """Send problem to Polygon.

    Args:
        problem_folder: Path to the problem folder.
        problem_id: ID of the Polygon problem.
    """
    verify_path(problem_folder)
    instance_paths(problem_folder)
    problem_id = check_polygon_id(problem_id)

    requests_list: List[Tuple[str, dict]] = get_requests_list()
    submit_requests_list(requests_list, problem_id)
