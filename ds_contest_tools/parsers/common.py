from typing import Union

from .. import logger, utils


def info_log(text: str) -> None:
    logger.info_log(text)


def validate_paths(problem_dir: Union[str, list], output_dir: str = '') -> None:
    utils.instance_paths(problem_dir, output_dir)
    if isinstance(problem_dir, list):
        for path in problem_dir:
            utils.verify_path(path)
    else:
        utils.verify_path(problem_dir)
