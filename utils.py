import os
import sys
from operator import mod
from metadata import Paths
from logger import setup_logger
from logger import error_log, debug_log
from subprocess import CompletedProcess


def convert_idx_to_string(idx: int) -> str:
    """Convert an integer to a string from
    alphabet [A-Z] using radix 26.
    """
    ans = ''
    while True:
        rem = mod(idx, 26)
        ans += chr(ord('A')+rem)
        idx //= 26
        if idx == 0:
            break
    return ans


def convert_to_bytes(x) -> bytes:
    """Convert a string to bytes."""
    if isinstance(x, bytes):
        return x
    return bytes(str(x), 'utf8')


def verify_command(p: CompletedProcess, message: str) -> None:
    """Check if the output of the function 'subprocess.run' is ok."""
    if p.returncode:
        error_log(p.stdout)
        error_log(p.stderr)
        print(message)
        sys.exit(1)

    if p.stdout and p.stdout != '':
        debug_log(p.stdout)
    if p.stderr and p.stderr != '':
        debug_log(p.stderr)


def instance_paths(problem_dir, output_dir='') -> None:
    """Initialize metadata dictionary and logs."""
    if (type(problem_dir) is list):
        problem_dir = [os.path.abspath(s) for s in problem_dir]
    else:
        problem_dir = os.path.abspath(problem_dir)
    output_dir = os.path.abspath(output_dir)
    Paths.instance(problem_dir, output_dir)
    setup_logger('tool', 'tool.log')
    setup_logger('debug', 'debug.log')


def verify_path(path: str) -> None:
    if not os.path.exists(path):
        print(f'{os.path.basename(path)} does not exist.')
        sys.exit(1)