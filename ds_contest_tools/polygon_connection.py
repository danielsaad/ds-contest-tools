import concurrent.futures
import hashlib
import io
import json
import multiprocessing
import os
import queue
import random
import string
import sys
import time
import zipfile
from typing import Dict, List, Optional, Tuple, Union

import requests

from .config import custom_key
from .jsonutils import parse_json, write_to_json
from .logger import debug_log, error_log, info_log
from .metadata import Paths
from .toolchain import get_manual_tests
from .utils import convert_to_bytes, verify_path

URL = 'https://polygon.codeforces.com/api/'
RETRIES = 3


class APICallError(Exception):
    pass


def submit_requests_list(requests_list: List[tuple], problem_id: str) -> None:
    """Submit an organized list of requests to Polygon.

    Args:
        requests_list: Organized list of requests to be made.
        problem_id: ID of the Polygon problem.
    """
    info_log('Submitting requests to Polygon')

    first_batch = []
    tests_batch = []
    last_batch = []
    conn = requests.Session()

    # Separate requests
    for method, params in requests_list:
        if method == 'problem.saveScript':
            last_batch.append((method, params))
        elif method == 'problem.saveTest':
            if 'testInput' in params:
                tests_batch.append((method, params))
            else:
                last_batch.append((method, params))
        else:
            first_batch.append((method, params))

    # Add authorization parameters and make requests
    first_batch = add_requests_info(problem_id, first_batch)
    for method, params in first_batch:
        single_api_connection(method, params, conn)

    # Make concurrent tests requests
    submit_concurrent_requests(problem_id, tests_batch)

    # Add authorization parameters and make requests
    last_batch = add_requests_info(problem_id, last_batch)
    for method, params in last_batch:
        single_api_connection(method, params, conn)

    conn.close()


def submit_concurrent_requests(problem_id: int, requests_batch: List[Tuple[str, dict]]) -> None:
    """Submit a list of requests to the Polygon API using concurrent requests.

    Args:
        problem_id: The ID of the problem to submit requests for.
        requests_batch: A list of tuples, where each tuple contains a method name 
        and a dictionary of parameters for that method.
    """
    if not requests_batch:
        return

    with multiprocessing.Manager() as manager:
        q = manager.Queue()
        process = multiprocessing.Process(
            target=print_ordered_requests, args=(q, ))
        process.start()

        # Split list into smaller sub-lists to avoid authentication expired error
        max_workers = max(os.cpu_count() // 3, 1)
        max_request_time = 7
        batch_size = (300 // max_request_time) * max_workers
        split_batches = [requests_batch[i:i+batch_size]
                         for i in range(0, len(requests_batch), batch_size)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for batche in split_batches:
                # Submit requests concurrently
                futures = [executor.submit(concurrent_api_connection, method, params, q)
                           for method, params in add_requests_info(problem_id, batche)]
                # Check for exceptions in completed futures
                for future in concurrent.futures.as_completed(futures):
                    if future.exception() is not None:
                        for f in futures:
                            if f != future and not f.done():
                                f.cancel()
                        process.join()
                        sys.exit(0)
        process.join()


def get_package_id(packages: List[dict]) -> int:
    """Get ID of the latest READY linux package.

    Args:
        packages: List of dictionaries containing information about
        the packages from Polygon.

    Returns:
        The ID of the latest READY linux package.
    """
    linux_packages = [p for p in packages if p['state']
                      == 'READY' and p['type'] == 'linux']
    if not any(linux_packages):
        error_log("There is not a ready linux package on Polygon.")
        sys.exit(1)

    most_recent_creation_time = max(
        p['creationTimeSeconds'] for p in linux_packages)
    package_id = next(
        p['id'] for p in linux_packages if p['creationTimeSeconds'] == most_recent_creation_time)

    return package_id


def download_package_polygon(problem_id: str) -> None:
    """Download zip package from Polygon.

    Args:
        problem_id: Polygon problem ID.
    """
    content: dict = json.loads(make_api_request(
        'problem.packages', dict(), problem_id))

    # Get the LATEST FULL package ID
    package_id: int = get_package_id(content['result'])

    # Get the package content from Polygon
    params: dict = {
        'packageId': package_id,
        'type': 'linux'
    }
    response: bytes = make_api_request(
        'problem.package', params, problem_id)

    # Convert bytes to zip file
    package = zipfile.ZipFile(io.BytesIO(response))
    package.extractall(Paths().get_output_dir())
    package.close()


def check_polygon_id(problem_id: Union[str, None]) -> str:
    """Check if the problem ID is already defined in metadata file.

    Args:
        problem_id: User input of the problem ID.

    Returns:
        The ID of the problem, if it is defined.
    """
    metadata_path = os.path.join(Paths().get_problem_dir(), 'problem.json')
    verify_path(metadata_path)
    problem_metadata = parse_json(metadata_path)

    if problem_id:
        problem_metadata['polygon_config']['id'] = problem_id
        write_to_json(metadata_path, problem_metadata)
        return problem_id

    if 'polygon_config' not in problem_metadata.keys():
        error_log('File problem.json does not have "polygon_config" key.')
        sys.exit(0)

    if not problem_metadata['polygon_config']['id']:
        error_log(
            'Problem ID is not defined. Specify it in the command line or in problem.json.')
        sys.exit(0)

    return problem_metadata['polygon_config']['id']


def add_requests_info(problem_id: str, requests_list: List[Tuple[str, dict]]) -> List[Tuple[str, dict]]:
    """Add authentication parameters to a list of requests.

    Args:
        requests_list: List of requests for Polygon.

    Returns:
        The updated list with authentication parameters.
    """
    tool_path: str = os.path.dirname(os.path.abspath(__file__))
    keys: dict = parse_json(os.path.join(tool_path, 'secrets.json'))

    updated_requests_list: list = []
    for method, params in requests_list:
        method_params = add_auth_parameters(
            method, params, problem_id, keys['apikey'], keys['secret'])
        updated_requests_list.append((method, method_params))

    return updated_requests_list


def get_apisig(method_name: str, secret: str, params: dict) -> bytes:
    """Generate 'apiSig' value for the API authorization.

    Args:
        method_name: The method which will be called.
        secret: Secret key used to make the connection.
        params: Parameters of the method.

    Returns:
        Return the API signature value in bytes.
    """
    rand: str = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=6))
    rand: bytes = convert_to_bytes(rand)

    param_list: dict = [(convert_to_bytes(key), params[key]) for key in params]
    param_list.sort()

    apisig: bytes = rand + b'/' + convert_to_bytes(method_name) + b'?'
    apisig += b'&'.join([param[0] + b'=' + param[1] for param in param_list])
    apisig += b'#' + convert_to_bytes(secret)

    hash_sig: bytes = convert_to_bytes(hashlib.sha512(apisig).hexdigest())
    return rand + hash_sig


def add_auth_parameters(method: str, params: Dict[str, bytes], problem_id: str, api_key: str, secret_key: str) -> Dict[str, bytes]:
    """Add authentication parameters in request for Polygon API connection.

    Args:
        method: The method which will be called.
        params: Parameters of the method.
        problem_id: ID of the Polygon problem.
        api_key: API key used to make the connection.
        secret_key: Secret key used to make the connection.

    Returns:
        A dictionary containing the methods and parameters.
    """
    auth_params: dict = {
        'apiKey': api_key,
        'time': int(time.time()),
        'problemId': problem_id,
    }
    auth_params.update(params)

    for key in auth_params:
        auth_params[key] = convert_to_bytes(auth_params[key])
    auth_params['apiSig'] = get_apisig(method, secret_key, auth_params)

    return auth_params


def make_api_request(method: str, parameters: dict, problem_id: str) -> bytes:
    """Make a request to the Polygon API and return the response content.

    Args:
        method: The name of the API method to call.
        params: A dictionary of parameters to include in the API request.
        problem_id: The ID of the problem to target.

    Returns:
        The response content, as bytes.
    """
    tool_path = os.path.dirname(os.path.abspath(__file__))
    keys = parse_json(os.path.join(tool_path, 'secrets.json'))

    request_params = add_auth_parameters(
        method, parameters, problem_id, keys['apikey'], keys['secret'])

    response = single_api_connection(method, request_params)
    return response.content


def get_method_information(method: str, params: dict) -> str:
    """Get information about a given method.

    Args:
        method: The name of the method to retrieve information for.
        params: Dictionary of parameters used for requests to improve the information.

    Returns:
        A message containing information about the method.
    """
    method_messages = {
        'problem.updateInfo': 'General informations saved',
        'problem.saveTags': 'Tags saved',
        'problem.setInteractor': 'Interactor set',
        'problem.setChecker': 'Checker set',
        'problem.setValidator': 'Validator set',
        'problem.saveScript': 'Generator script saved',
        'problem.saveStatement': 'Statement text saved',
        'problem.info': 'Checking if problem is interactive',
        'problem.interactor': 'Checking interactor name',
        'problem.validator': 'Checking validator name',
        'problem.checker': 'Checking checker name',
        'problem.packages': 'Finding the latest linux package',
        'problem.package': 'Downloading ready package'
    }

    if method in method_messages:
        return method_messages[method]

    named_methods = {
        'problem.saveSolution': f'Solution',
        'problem.saveFile': f'File',
        'problem.saveStatementResource': f'Statement resource'
    }

    if method in named_methods:
        return f'{named_methods[method]} {str(params["name"].decode())} saved'

    if method == 'problem.saveTest':
        if 'testInput' in params:
            return f'Manual testcase {str(params["testIndex"].decode().lstrip("0"))} saved'
        return f'Testcase {str(params["testIndex"].decode()).lstrip("0")} set as statement example.'

    return 'No information about this method.'


def print_ordered_requests(q: multiprocessing.Queue) -> None:
    """Print the requests in order.

    Args:
        q: Queue with the requests.
        max_indice: Maximum indice of the requests.
    """
    tmp_folder = os.path.join(Paths().get_tmp_output_dir(), 'scripts')
    os.makedirs(tmp_folder, exist_ok=True)
    indexes: list = [os.path.basename(f) for f in get_manual_tests(tmp_folder)]
    indexes.sort(key=custom_key)

    pq = queue.PriorityQueue()

    index = 0
    while True:
        if index == len(indexes):
            break
        try:
            element = q.get(block=False)
        except:
            time.sleep(0.5)
            continue
        try:
            pq.put(int(element))
        except ValueError:
            error_log(element)
            break

        while not pq.empty() and str(pq.queue[0]) == str(indexes[index]):
            pq.get()
            info_log(f'Manual testcase {indexes[index]} saved')
            index += 1


def verify_response(response: requests.Response, params: Dict[str, List[bytes]]) -> str:
    """Verify if the request from Polygon was successful.

    Args:
        response: Response object returned from the request.
        params: Parameters used in the request.

    Returns: 
        A string with informations about the request
    """
    response_information = ['Request informations:']
    try:
        content = json.loads(response.content.decode())
        response_information.append(f"    API status: {content['status']}")
        response_information.append(f"    Comment: {content['comment']}")

        debug_log("API status: " + content['status'])
    except:
        response_information.append(
            "    Status code: " + str(response.status_code))

    parameters = 'Parameters:\n'
    for key, value in params.items():
        parameters += f"{key}: {value}\n"

    response_information.append('Check debug.log for parameters information')
    debug_log(parameters)

    return '\n'.join(response_information)


def concurrent_api_connection(method: str, request_params: dict, q) -> None:
    """Make concurrent requests for problem.saveTest method

    Args:
        method: Method to be used for the connection with the API
        request_params: Parameters used in the request
        q: Queue to sort the output messages

    Raises:
        APICallError: Internal server error from the API side
    """
    test_index = str(request_params['testIndex'].decode()).lstrip('0')

    # Make three attempts to connect to the API
    for retry in range(RETRIES):
        debug_log(f'Retry {retry + 1} for testcase {test_index}')
        response = requests.post(URL + method, files=request_params)

        if response.status_code == requests.codes.ok:
            q.put(test_index)
            return
        elif response.status_code == requests.codes.bad_request:
            q.put(f"Error submitting testcase {test_index}. Stopping requests\n"
                  + verify_response(response, request_params))
            raise APICallError

    q.put(f"Internal server error occurred while trying to submit {test_index} testcase. Try again\n"
          + verify_response(response, request_params))
    raise APICallError


def single_api_connection(method: str, request_params: dict, session: Optional[requests.Session] = None) -> requests.Response:
    """Make connection with the Polygon API.

    Args:
        method: The method to call.
        request_params: A dictionary of parameters to include in the API request.
        session: Session to make the requests.

    Returns:
        The response object from the API.
    """
    for retry in range(RETRIES):
        debug_log(f'Retry {retry + 1} for method {method}')
        try:
            if session == None:
                response = requests.post(URL + method, files=request_params)
            else:
                response = session.post(URL + method, files=request_params)
        except ConnectionResetError:
            error_log(f"Connection reset error occurred while making the API request. Try again.\n"
                      + verify_response(response, request_params))
            sys.exit(0)

        if response.status_code == requests.codes.ok:
            info_log(get_method_information(method, request_params))
            return response
        elif response.status_code == requests.codes.bad_request:
            error_log(f"Error submitting {method} method. Stoping requests.\n"
                      + verify_response(response, request_params))
            sys.exit(0)

    error_log("Internal server error occurred while making the API request. Try again.\n"
              + verify_response(response, request_params))
    sys.exit(0)
