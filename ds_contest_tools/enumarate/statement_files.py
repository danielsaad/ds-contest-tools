
from enum import Enum
import os


class StatementFiles(Enum):
    """
    Represents the LaTeX source files that compose a problem statement.

    Each member holds the file's base name and its extension. Use `filename`
    to get both concatenated.

    Attributes:
        DESCRIPTION: the problem description.
        INPUT: the input format section.
        OUTPUT: the output format section.
        NOTES: the notes section.
        TUTORIAL: the editorial of the problem.
        INTERACTOR: the interaction protocol, only for interactive problems.
    """
    DESCRIPTION = ('description', '.tex')
    INPUT = ('input', '.tex')
    OUTPUT = ('output', '.tex')
    NOTES = ('notes', '.tex')
    TUTORIAL = ('tutorial', '.tex')
    INTERACTOR = ('interactor', '.tex')

    def __init__(self, name: str, extension: str) -> None:
        self.file_name = name
        self.extension = extension

    @property
    def filename(self) -> str:
        """Return the file name with its extension."""
        return self.file_name + self.extension
