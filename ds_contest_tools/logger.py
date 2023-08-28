import io
import logging
import os
import sys

from .metadata import Paths


class tcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """Setup a logger with the specified name, log file, and logging level.

    Args:
        name: The name of the logger.
        log_file: The path to the log file.
        level: The logging level. Defaults to logging.DEBUG.

    Returns:
        A logger object with the specified configurations.
    """
    old_cwd = os.getcwd()
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Generate log inside problem/contest directory
    directory = Paths().get_problem_dir()
    if isinstance(directory, list):
        directory = Paths().get_output_dir()
    try:
        os.makedirs(directory, exist_ok=True)
    except PermissionError:
        print(f'Permission denied. Could not create folder in {directory}.')
        sys.exit()
    os.chdir(directory)

    # Log configurations
    try:
        handler = logging.FileHandler(log_file, mode='w')
    except PermissionError:
        print(f'Permission denied. Could not create log file in {directory}')
        sys.exit(0)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    os.chdir(old_cwd)
    return logger


def convert_to_string(x) -> str:
    """Converts x to string.

    Args:
        x: Object to be converted to string.

    Returns:
        The string representation of x.
    """
    if isinstance(x, bytes):
        try:
            return x.decode('utf-8').rstrip()
        except UnicodeDecodeError:
            pass
    elif isinstance(x, io.BufferedReader):
        return ""
    try:
        x = str(x)
        return x.rstrip()
    except:
        pass
    return ""


def info_log(text: str) -> None:
    """Logs information about the tool.

    Args:
        text: The information to be logged.
    """
    tool = logging.getLogger('tool')
    info = convert_to_string(text)
    if len(info) > 0:
        tool.info(info)
        print(f"{tcolors.OKGREEN}{text}{tcolors.ENDC}")


def warning_log(text: str) -> None:
    """Logs warnings about the tool.

    Args:
        text: The warning information to be logged.
    """
    tool = logging.getLogger('tool')
    info = convert_to_string(text)
    if len(info) > 0:
        tool.warning(info)
        print(f"{tcolors.WARNING}{text}{tcolors.ENDC}")


def debug_log(text: str) -> None:
    """Logs debug information about the tool.

    Args:
        text: The debug information to be logged.
    """
    debug = logging.getLogger('debug')
    info = convert_to_string(text)
    if len(info) > 0:
        debug.info(info)


def error_log(text: str) -> None:
    """Logs errors that occur during tool execution.

    Args:
        text: The error information to be logged.
    """
    tool = logging.getLogger('tool')
    info = convert_to_string(text)
    if len(info) > 0:
        tool.error(info)
        print(f"{tcolors.FAIL}{text} Exiting...{tcolors.ENDC}")
        sys.exit(0)