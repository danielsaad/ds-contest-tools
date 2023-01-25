import logging
import os
from metadata import Paths


formatter = logging.Formatter('%(levelname)s - %(message)s')


def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """To setup as many loggers as you want"""
    old_cwd = os.getcwd()

    if (type(Paths.instance().dirs['problem_dir']) is list):
        os.makedirs(Paths.instance().dirs['output_dir'], exist_ok=True)
        os.chdir(Paths.instance().dirs['output_dir'])
    else:
        os.makedirs(Paths.instance().dirs['problem_dir'], exist_ok=True)
        os.chdir(Paths.instance().dirs['problem_dir'])

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
    tool.info(text.rstrip())


def debug_log(text: str) -> None:
    """Print informations of subprocesses of the tool to a log."""
    debug = logging.getLogger('debug')
    debug.debug(text.rstrip())


def error_log(text: str) -> None:
    """Print errors to a log."""
    tool = logging.getLogger('tool')
    tool.error(text.rstrip())
