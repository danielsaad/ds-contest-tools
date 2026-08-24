
from enum import Enum


class ProblemAnswer(Enum):
    """
    Enumerates the possible answers to a problem.

    Attributes:
        CORRECT (bool): Represents a correct answer.
        WRONG (bool): Represents an incorrect answer.
    """
    CORRECT = True
    WRONG = False