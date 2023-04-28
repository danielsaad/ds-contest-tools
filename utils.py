import os
import sys
from datetime import datetime
from operator import mod
from subprocess import CompletedProcess
from typing import Optional, Union

from logger import debug_log, error_log, info_log, setup_logger
from metadata import Paths


def convert_idx_to_string(idx: int) -> str:
    """
    Convert an integer to a string from alphabet [A-Z] using radix 26.

    Args:
        idx (int): The integer to be converted.

    Returns:
        str: The string representing the integer in base 26.
    """
    ans: str = ''
    while True:
        rem: int = mod(idx, 26)
        ans += chr(ord('A')+rem)
        idx //= 26
        if idx == 0:
            break
    return ans


def convert_to_bytes(x) -> bytes:
    """
    Convert a string to bytes.

    Args:
        x: The string to be converted.

    Returns:
        bytes: The bytes representation of the string.
    """
    if isinstance(x, bytes):
        return x
    return bytes(str(x), 'utf8')


def check_subprocess_output(p: CompletedProcess, message: str) -> None:
    """
    Check if the output of the function 'subprocess.run' is ok.

    Args:
        p (CompletedProcess): The completed process returned by the 'subprocess.run' function.
        message (str): The message to be printed in case of an error.
    """
    if p.returncode:
        error_log(p.stdout, print_text=False)
        error_log(p.stderr, print_text=False)
        error_log(message)
        sys.exit(1)

    if p.stdout and p.stdout != '':
        debug_log(p.stdout)
    if p.stderr and p.stderr != '':
        debug_log(p.stderr)


def instance_paths(problem_dir: Union[str, list], output_dir: Optional[str] = '') -> None:
    """
    Initialize metadata dictionary and logs.

    Args:
        problem_dir (Union[str, list]): The path(s) to the problem directory(ies).
        output_dir (Optional[str]): The path to the output directory.
    """
    if isinstance(problem_dir, list):
        problem_dir = [os.path.abspath(s) for s in problem_dir]
    else:
        problem_dir = os.path.abspath(problem_dir)
    output_dir = os.path.abspath(output_dir) if output_dir else ''

    Paths(problem_dir, output_dir)
    setup_logger('tool', 'tool.log')
    setup_logger('debug', 'debug.log')


def verify_solutions(solutions_dict: dict) -> None:
    """
    Verify if solutions exists in the src folder.

    Args:
        solutions_dict (dict): Dictionary containing the solutions of the problem.
    """
    problem_folder: Union[list, str] = Paths().get_problem_dir()
    for _, solutions in solutions_dict.items():
        # Ignore verification due to creation of contest
        if isinstance(problem_folder, list):
            break
        # Verify main solution
        if isinstance(solutions, str):
            verify_path(os.path.join(problem_folder, 'src', solutions))
            continue
        # Verify others solutions
        for file in solutions:
            verify_path(os.path.join(problem_folder, 'src', file))


def check_problem_metadata(problem_metadata: dict) -> None:
    """
    Check variables inside problem.json for type errors.

    Args:
        problem_metadata (dict): The problem.json file as a dictionary.
    """
    verify_solutions(problem_metadata['solutions'])

    expected_types = {
        'problem': {'time_limit': int, 'memory_limit_mb': int, 'interactive': bool},
        'io_samples': int
    }
    for key in expected_types:
        if key not in problem_metadata:
            error_log(f"Variable {key} is not defined in problem.json.")
            sys.exit(1)

        if key == 'io_samples':
            if not isinstance(problem_metadata[key], expected_types[key]):
                error_log(
                    f"Variable '{key}' is not a(n) {expected_types[key].__name__}.")
                sys.exit(1)
            continue

        for subkey, expected_type in expected_types[key].items():
            value = problem_metadata[key].get(subkey)
            if not isinstance(value, expected_type):
                error_log(
                    f"Variable '{subkey}' in '{key}' is not a(n) {expected_type.__name__}.")
                sys.exit(1)


def verify_path(path: str) -> None:
    """
    Verify if path exists in folder.

    Args:
        path (str): Path to the file.
    """
    if not os.path.exists(path):
        error_log(f'{os.path.relpath(path)} does not exist.')
        sys.exit(1)


def generate_timestamp() -> str:
    """
    Generate a timestamp in the format (Day-Month-Year-Hour:Minute:Seconds)

    Returns:
        The string representing the timestamp.
    """
    current_time: datetime = datetime.fromtimestamp(datetime.now().timestamp())
    timestamp: str = current_time.strftime('%Y-%m-%d-%H:%M:%S')
    return timestamp


def generate_tmp_directory() -> str:
    """Generate path to a temporary directory.

    Returns:
        Path to the temporary directory.
    """
    return os.path.join('/', 'tmp', f'ds-contest-tools-{generate_timestamp()}')
