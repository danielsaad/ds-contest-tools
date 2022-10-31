import os


class Paths:

    _instance = None

    def __init__(self, problem_dir, output_dir):
        self.dirs = {
            "tool_dir": os.path.dirname(os.path.relpath(__file__)),
            "problem_dir": problem_dir,
            "output_dir": output_dir
        }

    @classmethod
    def instance(cls, problem_dir='', output_dir=''):
        if cls._instance is None:
            cls._instance = cls(problem_dir, output_dir)
        return cls._instance
