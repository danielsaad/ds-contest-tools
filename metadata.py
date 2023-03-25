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
        dirs: A dictionary containing the paths to the problem and output directories.

    Methods:
        get_problem_dir() -> Union[str, list]: Returns the path to the problem directory.
        get_output_dir() -> str: Returns the path to the output directory.
    """

    def __init__(self, problem_dir: Union[str, list], output_dir: str):
        """Initializes the necessary attributes for the instance.

        Args:
            problem_dir : The path to the problem(s) directory(ies).
            output_dir: The path to the output directory.
        """
        self.dirs: dict = {
            "problem_dir": problem_dir,
            "output_dir": output_dir
        }

    def get_problem_dir(self) -> Union[str, list]:
        """Get the problem directory."""
        return self.dirs["problem_dir"]

    def get_output_dir(self) -> str:
        """Get the output directory."""
        return self.dirs["output_dir"]
