
from enum import Enum


class Status(Enum):
    """
    Represents the status of an algorithm's execution on a given test case.

    Attributes:
        AC: represents an Accepted status.
        WA: represents a Wrong Answer status.
        RE: represents a Runtime Error status.
        MLE: represents a Memory Limit Exceeded status.
        HARD_TLE: represents a Hard Time Limit Exceeded status.
        SOFT_TLE: represents a Soft Time Limit Exceeded status.
        PE: represents a Presentation Error status.
        AC_TLE: represents an Accepted with Time Limit Exceeded status.
        TLE_MLE: represents a Time Limit Exceeded with Memory Limit Exceeded status.
        FAIL: represents a General Failure status.
    """
    AC = 0
    WA = 1
    RE = 2
    MLE = 3
    HARD_TLE = 4
    SOFT_TLE = 5
    PE = 6
    AC_TLE = 7
    TLE_MLE = 8
    FAIL = 9