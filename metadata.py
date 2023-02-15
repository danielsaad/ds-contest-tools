class Paths:
    """A class to store the most used paths of the tool."""
    _instance = None

    def __init__(self, problem_dir, output_dir):
        """Construct all the necessary attributes for the instance."""
        self.dirs = {
            "problem_dir": problem_dir,
            "output_dir": output_dir
        }

    @classmethod
    def instance(cls, problem_dir='', output_dir=''):
        """Start a singleton class."""
        if cls._instance is None:
            cls._instance = cls(problem_dir, output_dir)
        return cls._instance
