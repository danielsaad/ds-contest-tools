import os
from dataclasses import dataclass
from sys import exit
from typing import Union


def singleton(cls):
    """Decorator to create a Singleton class.

    Args:
        cls: The class to decorate.

    Returns:
        A function that returns a singleton instance of the given class.
    """
    instances: dict = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class Paths:
    """A class to store the most commonly used paths of the tool.

    Attributes:
        problem_dir (Union[str, list]): The path to the problem(s) directory(ies).
        output_dir (str): The path to the output directory.
        tmp_output_dir (str): The path to the root of the temporary output directory.

    Methods:
        get_problem_dir() -> Union[str, list]: Returns the path to the problem directory.
        get_output_dir() -> str: Returns the path to the output directory.
    """

    def __init__(self, problem_dir: Union[str, list], output_dir: str, tmp_output_root_dir: str) -> None:
        """Initializes the necessary attributes for the instance.

        Args:
            problem_dir : The path to the problem(s) directory(ies).
            output_dir: The path to the output directory.
            tmp_output_root_dir: The path to the root of the temporary output directory
        """
        self.__problem_dir: Union[str, list] = problem_dir
        self.__output_dir: str = output_dir
        self.__tmp_output_dir: str = tmp_output_root_dir

    def get_problem_dir(self) -> Union[str, list]:
        """Get the problem directory."""
        return self.__problem_dir

    def get_output_dir(self) -> str:
        """Get the output directory."""
        return self.__output_dir

    def get_tmp_output_dir(self) -> str:
        """Get the temporary output root directory"""
        return self.__tmp_output_dir

    def set_output_dir(self, output_dir: str) -> None:
        """Set the output directory"""
        self.__output_dir = output_dir
