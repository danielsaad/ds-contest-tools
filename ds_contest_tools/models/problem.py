from typing import TYPE_CHECKING
from ds_contest_tools.logger import error_log

if TYPE_CHECKING:
    from ds_contest_tools.models.solution import Solution

class Problem:
    """
    Represents a problem to be solved by one or more algorithms.

    Attributes:
        problem_name: The name of the problem.
        time_limit: The maximum time allowed for each algorithm's execution in seconds.
        memory_limit: The maximum memory limit allowed for each algorithm in bytes.
        solutions: A list of solutions for the problem.

    Methods:
        problem_name() -> str
        problem_dir() -> str
        input_folder() -> str
        time_limit() -> float
        memory_limit() -> float
        add_solution(solution: 'Solution') -> None
        get_list_solution() -> list
        get_number_of_solutions() -> int
        is_solution_list_empty() -> bool
    """

    def __init__(self, problem_name: str, problem_dir: str, input_folder: str, time_limit: float, memory_limit: float) -> None:
        """
        Initializes a new instance of the Problem class.

        Args:
            problem_name: The name of the problem.
            time_limit: The maximum time allowed for each algorithm's execution in seconds.
            memory_limit: The maximum memory limit allowed for each algorithm in bytes.

        """
        self.__problem_name = problem_name
        self.__problem_dir = problem_dir
        self.__input_folder = input_folder
        self.__time_limit = time_limit
        self.__memory_limit = memory_limit * 1000000
        self.__solutions: list['Solution'] = []

    @property
    def problem_name(self) -> str:
        """
        Get the problem name

        Returns:
            str: problem name
        """

        return self.__problem_name

    @property
    def problem_dir(self) -> str:
        """
        Get the problem directory

        Returns:
            str: problem directory
        """
        return self.__problem_dir

    @property
    def input_folder(self) -> str:
        """
        Get the input folder

        Returns:
            str: input folder
        """
        return self.__input_folder

    @property
    def time_limit(self) -> float:
        """
        Get the maximum time allowed for each algorithm's execution in seconds.

        Returns:
            float: The maximum time allowed for each algorithm's execution in seconds.

        """
        return self.__time_limit

    @property
    def memory_limit(self) -> float:
        """
        Get the maximum memory limit allowed for each algorithm in bytes.

        Returns:
            float: The maximum memory limit allowed for each algorithm in bytes.
        """
        return self.__memory_limit

    def add_solution(self, solution: 'Solution') -> None:
        """
        Adds a new solution to the list of solutions for this problem.

        Args:
            solution: A Solution object representing the new solution to add.

        """
        self.__solutions.append(solution)

    def get_list_solution(self) -> list:
        """
        Returns a list of all solutions associated with this problem.

        Returns:
            list: A list of Solution objects.

        """
        return self.__solutions

    def get_number_of_solutions(self) -> int:
        """
        Returns the number of solutions associated with this problem.

        Returns:
            int: The number of solutions associated with this problem.

        """
        return len(self.__solutions)

    def is_solution_list_empty(self) -> bool:
        """
        Returns True if there are no solutions associated with this problem.

        Returns:
            bool: True if there are no solutions associated with this problem, False otherwise.

    """
        return self.get_number_of_solutions() == 0

    def get_number_of_tests(self) -> int:
        """
        Get the number of tests of a given problem

        Returns:
            int: The number of tests
        """
        try:
            solution: 'Solution' = self.get_list_solution()[0]
        except:
            error_log(
                f'The solution list for problem {self.problem_name} is empty.')
        return len(solution.tests)