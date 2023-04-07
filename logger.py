import logging
import os

from metadata import Paths


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
    os.makedirs(directory, exist_ok=True)
    os.chdir(directory)

    # Log configurations
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    os.chdir(old_cwd)
    return logger


def info_log(text: str) -> None:
    """Logs information about the tool.

    Args:
        text: The information to be logged.
    """
    tool = logging.getLogger('tool')
    text = text.rstrip()
    if text is not None and text != '':
        tool.info(text)
        print(text)


def debug_log(text: str) -> None:
    """Logs debug information about the tool.

    Args:
        text: The debug information to be logged.
    """
    debug = logging.getLogger('debug')
    if text is not None and text.rstrip() != '':
        debug.debug(text.rstrip())


def error_log(text: str, print_text: bool = True) -> None:
    """Logs errors that occur during tool execution.

    Args:
        text: The error information to be logged.
    """
    tool = logging.getLogger('tool')
    text = text.rstrip()
    if text is not None and text != '':
        tool.error(text)
        if print_text:
            print(text)
        
