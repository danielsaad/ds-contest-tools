import hashlib
import io
import json
import os
import random
import string
import sys
import time
import zipfile
from typing import Dict, List, Optional, Tuple, Union

import requests

from jsonutils import parse_json, write_to_json
from logger import debug_log, error_log, info_log
from metadata import Paths
from utils import convert_to_bytes, verify_path

URL = 'https://polygon.codeforces.com/api/'


def submit_requests_list(requests_list: List[dict]) -> None:
    """
    Submits a list of requests to the Polygon API using a single connection.

    Args:
        requests_list: A list of dictionaries containing the method and parameters
                       for each request.
    """
    conn = requests.Session()
    for method, params in requests_list:
        make_api_connection(method, params, conn)


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
        print("There is not a ready linux package on Polygon.")
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
        print('File problem.json does not have "polygon_config" key.')
        sys.exit(0)

    if not problem_metadata['polygon_config']['id']:
        print(
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


def verify_response(response: requests.Response, method: str, params: Dict[str, List[bytes]]) -> None:
    """Verify if the request from Polygon was successful.

    Args:
        response: Response object returned from the request.
        method: The method used in the request.
        params: Parameters used in the request.
    """
    if response.status_code == requests.codes.ok:
        info_log(f'Request {method} successfull.')
    elif response.status_code == requests.codes.bad_request:
        content = json.loads(response.content.decode())
        parameters = 'Parameters:\n'
        for key, value in params.items():
            parameters += f"{key}: {str(value)}\n"

        error_log(f"API status: {content['status']}")
        error_log(f"Comment: {content['comment']}")
        error_log('Check debug.log for parameters information')

        debug_log("API status: " + content['status'])
        debug_log(parameters)

        print(f"Wrong parameter of {method} method.")
        sys.exit(1)
    else:
        print("Could not connect to the API.")
        sys.exit(1)


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

    response = make_api_connection(method, request_params)
    return response.content


def make_api_connection(method: str, request_params: dict, session: Optional[requests.Session] = None) -> requests.Response:
    """Make connection with the Polygon API.

    Args:
        method: The method to call.
        request_params: A dictionary of parameters to include in the API request.
        session: Session to make the requests.

    Returns:
        The response object from the API.
    """
    if session == None:
        response = requests.post(URL + method, files=request_params)
    else:
        response = session.post(URL + method, files=request_params)
    verify_response(response, method, request_params)

    return response
