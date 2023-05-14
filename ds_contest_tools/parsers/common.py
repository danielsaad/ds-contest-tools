import os.path
import sys
from typing import Union

from .. import logger, utils


def error_log(text: str) -> None:
    """Log an error.

    Args:
        text: Text to be logged.
    """
    logger.error_log(text)


def info_log(text: str) -> None:
    """Log information about the tool.

    Args:
        text: Text to be logged.
    """
    logger.info_log(text)


def get_basename(path: str) -> str:
    """Get the basename of a path.

    Args:
        path: The path to the file.

    Returns:
        The basename of the path.
    """
    return os.path.basename(path)


def setup_and_validate_paths(problem_dir: Union[str, list], output_dir: str = '', verify_path: bool = True) -> None:
    """Instance logger and verify paths.

    Args:
        problem_dir: Path(s) to the problem directory(ies)
        output_dir: Path to the output directory. Defaults to ''.
    """
    if verify_path:
        if isinstance(problem_dir, list):
            for path in problem_dir:
                if not os.path.exists(path):
                    print(f'Problem {path} does not exist')
                    sys.exit(1)
        elif not os.path.exists(problem_dir):
            print(f'Problem {problem_dir} does not exist.')
            sys.exit(1)
        
    utils.instance_paths(problem_dir, output_dir)

