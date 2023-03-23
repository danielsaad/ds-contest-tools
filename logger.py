import os
import logging
from metadata import Paths


def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """Setup as many loggers as needed"""
    old_cwd = os.getcwd()
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Generate log inside problem directory
    if type(Paths().get_problem_dir()) is list:
        os.makedirs(Paths().get_output_dir(), exist_ok=True)
        os.chdir(Paths().get_output_dir())
    else:
        os.makedirs(Paths().get_problem_dir(), exist_ok=True)
        os.chdir(Paths().get_problem_dir())

    # Log configurations
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    os.chdir(old_cwd)
    return logger


def info_log(text: str) -> None:
    """Print informations of the tool to a log."""
    tool = logging.getLogger('tool')
    if text is not None:
        tool.info(text.rstrip())


def debug_log(text: str) -> None:
    """Print debug informations of the tool to a log."""
    debug = logging.getLogger('debug')
    if text is not None:
        debug.debug(text.rstrip())


def error_log(text: str) -> None:
    """Print errors of the tool to a log."""
    tool = logging.getLogger('tool')
    if text is not None:
        tool.error(text.rstrip())
