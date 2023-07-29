import os
import sys
from datetime import datetime
from operator import mod
from subprocess import CompletedProcess
from typing import Optional, Union

from .logger import convert_to_string, debug_log, error_log, setup_logger
from .metadata import Paths


def convert_idx_to_string(idx: int) -> str:
    """Convert an integer to a string from alphabet [A-Z] using radix 26.

    Args:
        idx (int): The integer to be converted.

    Returns:
        The string representing the integer in base 26.
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
    """Convert a string to bytes.

    Args:
        x: The string to be converted.

    Returns:
        The bytes representation of the string.
    """
    if isinstance(x, bytes):
        return x
    return bytes(str(x), 'utf8')


def check_subprocess_output(p: CompletedProcess, message: str) -> None:
    """Check if the output of the function 'subprocess.run' is ok.

    Args:
        p: The completed process returned by the 'subprocess.run' function.
        message: The message to be printed in case of an error.
    """
    stdout = convert_to_string(p.stdout)
    stderr = convert_to_string(p.stderr)
    if len(stdout) > 0:
        debug_log(stdout)
    if len(stderr) > 0:
        debug_log(stderr)

    if p.returncode:
        error_log(f"{message} (return code: {p.returncode}).")


def instance_paths(problem_dir: Union[str, list], output_dir: Optional[str] = '') -> None:
    """Initialize metadata dictionary and logs.

    Args:
        problem_dir: The path(s) to the problem directory(ies).
        output_dir: The path to the output directory.
    """
    if isinstance(problem_dir, list):
        problem_dir = [os.path.abspath(s) for s in problem_dir]
    else:
        problem_dir = os.path.abspath(problem_dir)
    output_dir = os.path.abspath(output_dir) if output_dir else ''
    tmp_output_root_dir = os.path.join(
        '/', 'tmp', f'ds-contest-tools-{generate_timestamp()}')
    Paths(problem_dir, output_dir, tmp_output_root_dir)
    setup_logger('tool', 'tool.log')
    setup_logger('debug', 'debug.log')


def verify_solutions(solutions_dict: dict) -> None:
    """Verify if solutions exists in the src folder.

    Args:
        solutions_dict: Dictionary containing the solutions of the problem.
    """
    problem_folder: Union[list, str] = Paths().get_problem_dir()
    # Ignore verification due to creation of contest
    if isinstance(problem_folder, list):
        return
    for _, solutions in solutions_dict.items():
        # Verify main solution
        if isinstance(solutions, str):
            verify_path(os.path.join(problem_folder, 'src', solutions))
            verify_file(os.path.join(problem_folder, 'src', solutions))
            verify_supported_languages(solutions)
            continue
        # Verify others solutions
        for file in solutions:
            verify_path(os.path.join(problem_folder, 'src', file))
            verify_file(os.path.join(problem_folder, 'src', file))
            verify_supported_languages(file)


def verify_file(filepath: str) -> None:
    if not os.path.isfile(filepath):
        error_log(f'Solution in problem.json cannot be empty.')


def verify_supported_languages(solution_file: str):
    suported_languages: dict[str, bool] = {
        'c': True,
        'cpp': True,
        'java': True,
        'py': True
    }
    _, ext = solution_file.split('.')
    if not suported_languages.get(ext, False):
        error_log(
            f'Programming language for solution {solution_file} is not supported or has an invalid extension')


def check_problem_metadata(problem_metadata: dict) -> None:
    """Check variables inside problem.json for type errors.

    Args:
        problem_metadata: The problem.json file as a dictionary.
    """
    verify_solutions(problem_metadata['solutions'])

    expected_types = {
        'problem': {'time_limit': int, 'memory_limit_mb': int, 'interactive': bool},
        'io_samples': int
    }
    for key in expected_types:
        if key not in problem_metadata:
            error_log(f"Variable {key} is not defined in problem.json.")

        if key == 'io_samples':
            if not isinstance(problem_metadata[key], expected_types[key]):
                error_log(
                    f"Variable '{key}' is not a(n) {expected_types[key].__name__}.")
            continue

        for subkey, expected_type in expected_types[key].items():
            value = problem_metadata[key].get(subkey)
            if not isinstance(value, expected_type):
                error_log(
                    f"Variable '{subkey}' in '{key}' is not a(n) {expected_type.__name__}.")


def verify_path(path: str) -> None:
    """Verify if path exists in folder.

    Args:
        path: Path to the file.
    """
    if not os.path.exists(path):
        error_log(f'{os.path.relpath(path)} does not exist.')


def generate_timestamp() -> str:
    """Generate a timestamp in the format (Day-Month-Year-Hour:Minute:Seconds)

    Returns:
        The string representing the timestamp.
    """
    current_time: datetime = datetime.fromtimestamp(datetime.now().timestamp())
    timestamp: str = current_time.strftime('%Y-%m-%d-%H:%M:%S')
    return timestamp
