import sys
from operator import mod
from subprocess import CompletedProcess
from logger import error_log, debug_log

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
    
def verify_command(p: CompletedProcess, message: str) -> None:
    """Checks if the output of the function 'subprocess.run' is ok."""
    if (p.returncode):
        error_log(p.stdout)
        error_log(p.stderr)
        print(message)
        sys.exit(1)
    
    if (p.stdout):
        debug_log(p.stdout)
    if (p.stderr):
        debug_log(p.stderr)
