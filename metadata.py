from typing import Union


def singleton(cls):
    """Decorator to create a Singleton class."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class Paths:
    """A class to store the most used paths of the tool."""

    def __init__(self, problem_dir: Union[str, list], output_dir: str):
        """Construct all the necessary attributes for the instance."""
        self.dirs = {
            "problem_dir": problem_dir,
            "output_dir": output_dir
        }

    def get_problem_dir(self) -> Union[str, list]:
        """Get the problem directory."""
        return self.dirs["problem_dir"]

    def get_output_dir(self) -> str:
        """Get the output directory."""
        return self.dirs["output_dir"]
