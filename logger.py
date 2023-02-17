import os
import logging
from metadata import Paths


def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """Setup as many loggers as needed"""
    old_cwd = os.getcwd()
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Generate log inside problem directory
    if type(Paths.instance().dirs['problem_dir']) is list:
        os.makedirs(Paths.instance().dirs['output_dir'], exist_ok=True)
        os.chdir(Paths.instance().dirs['output_dir'])
    else:
        os.makedirs(Paths.instance().dirs['problem_dir'], exist_ok=True)
        os.chdir(Paths.instance().dirs['problem_dir'])

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
    tool.info(text)


def debug_log(text: str) -> None:
    """Print debug informations of the tool to a log."""
    debug = logging.getLogger('debug')
    debug.debug(text)


def error_log(text: str) -> None:
    """Print errors of the tool to a log."""
    tool = logging.getLogger('tool')
    tool.error(text)
