import os
import logging
import sys
from operator import mod
from subprocess import CompletedProcess


def convert_idx_to_string(idx: int) -> str:
    """Converts an integer to a string from
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


def start_log() -> None:
    """Create and configure log file."""
    old_cwd = os.getcwd()
    tool_path = os.path.dirname(os.path.relpath(__file__))
    if (tool_path != ''):
        os.chdir(tool_path)
    logging.basicConfig(filename="tool.log", 
                    format='%(levelname)s - %(message)s',
                    filemode='a',
                    encoding='utf-8', 
                    level=logging.DEBUG)
    os.chdir(old_cwd)


def verify_command(p: CompletedProcess, message: str) -> None:
    """Checks if the output of the function 'subprocess.run' is ok."""
    if (p.returncode):
        logging.error(p.stdout)
        logging.error(p.stderr)
        print(message)
        sys.exit(1)

    if (p.stdout != ''):
        logging.debug(p.stdout)
    if (p.stderr != ''):
        logging.debug(p.stderr)
