import logging
import os


formatter = logging.Formatter('%(levelname)s - %(message)s')


def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """To setup as many loggers as you want"""
    old_cwd = os.getcwd()
    tool_path = os.path.dirname(os.path.abspath(__file__))
    if (tool_path != ''):
        os.chdir(tool_path)

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    os.chdir(old_cwd)
    return logger


# first file logger
tool = setup_logger('tool', 'tool.log')


# second file logger
debug = setup_logger('debug', 'debug.log')


def info_log(text: str) -> None:
    tool.info(str(text))


def debug_log(text: str) -> None:
    debug.debug(str(text))


def error_log(text: str) -> None:
    tool.error(str(text))
