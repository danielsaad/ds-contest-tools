from dataclasses import dataclass


@dataclass
class Statistic:
    """
    Represents a statistical summary of a solution.

    Attributes:
        ac_count: The count of accepted tests statuses.
        max_exec_time: The maximum execution time of a solution.
        max_memory_usage: The maximum memory usage of a solution.
    """
    ac_count: int = 0
    max_exec_time: float = 0.0
    max_memory_usage: float = 0.0