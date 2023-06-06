import os
from dataclasses import dataclass
from enum import Enum
from sys import exit
from typing import Union


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


class ProblemAnswer(Enum):
    """
    Enumerates the possible answers to a problem.

    Attributes:
        CORRECT (bool): Represents a correct answer.
        WRONG (bool): Represents an incorrect answer.
    """
    CORRECT = True
    WRONG = False


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
        self.__memory_limit = memory_limit * 2 ** 20
        self.__solutions: list[Solution] = []

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
        from .logger import info_log
        try:
            solution: Solution = self.get_list_solution()[0]
        except:
            info_log(
                f'The solution list for problem {self.problem_name} is empty.')
            exit(1)
        return len(solution.tests)


class Solution:
    """
    Represents a solution to a programming problem.

    Attributes:
        solution_name: The name of the solution file.
        expected_result: The expected result of running the solution.
        output_path: The path to the folder where the output files generated 
        solution_status: The status of the solution.
        statistics: The statistics of a given solution.
        exec_args: The command line arguments to be executed.
        tests: The dictionary of tests that were run on the solution.

    """

    def __init__(self, solution_name: str, expected_result: str) -> None:
        """
        Initializes a new instance of the Solution class.

        Args:
            solution_name: The name of the solution file.
            expected_result: The expected result of running the solution.

        """
        self.__solution_name: str = solution_name
        self.__expected_result: str = expected_result
        self.__output_path: str = self.__generate_output_folder()
        self.__solution_status: ProblemAnswer = None
        self.__statistics: Statistic = None
        self.__exec_args: list = None
        self.__tests: dict = {}

    @property
    def solution_name(self) -> str:
        """
        Gets the name of the solution file.

        Returns:
            str: The name of the solution file.

        """
        return self.__solution_name

    @property
    def expected_result(self) -> str:
        """
        Gets the expected result of running the solution.

        Returns:
            str: The expected result of running the solution.

        """
        return self.__expected_result

    @property
    def output_path(self) -> str:
        """
        Gets the path to the folder where the output files generated by the 
            solution are stored.

        Returns:
            The path to the folder where the output files generated by the
              solution are stored.

        """
        return self.__output_path

    @property
    def solution_status(self) -> ProblemAnswer:
        """
        Gets the status of the solution.

        Returns:
            Status: The status of the solution.
        """
        return self.__solution_status

    @solution_status.setter
    def solution_status(self, solution_status: ProblemAnswer) -> None:
        """
        Sets the solution status of the test case.

        Args:
            solution_status: The solution status to set.
        """
        self.__solution_status = solution_status

    @property
    def statistics(self) -> 'Statistic':
        """
        Gets the statistics (max execution time, max memory usage...) 
        of the solution

        Returns:
            Statistic: The statistics of the solution
        """
        return self.__statistics

    @statistics.setter
    def statistics(self, statistics: 'Statistic') -> None:
        """
        Sets the statistics information for a given problem

        Args:
            statistics: The statistics information to set
        """
        self.__statistics = statistics

    @property
    def exec_args(self) -> list:
        """
        Gets the command line arguments to be executed

        Returns:
            list: A list of the arguments
        """
        return self.__exec_args

    @exec_args.setter
    def exec_args(self, exec_args: str) -> None:
        """
        Sets the command line arguments

        Args:
            exec_args: A string of line arguments divided by spaces
        """
        self.__exec_args = exec_args.split()

    @property
    def tests(self) -> dict:
        """
        Gets the dictionary of tests that were run on the solution.

        Returns:
            dict: The dictionary of tests that were run on the solution.
        """
        return self.__tests

    def add_tests(self, tests: dict) -> None:
        """
        Adds a dictionary of tests to the dictionary of tests that were run 
            on the solution.

        Args:
            test: The dictionary with the tests to add.
        """
        self.__tests = tests

    def get_binary_name(self) -> str:
        """
        Returns the name of the binary file generated from the solution.

        Args:
            solution_name: The name of the solution file.

        Returns:
            str: The name of the binary file generated from the solution.
        """
        file_name, _ = os.path.splitext(self.__solution_name)
        return file_name

    def get_file_extension(self) -> str:
        """
        Returns the extension of the solution file.

        Args:
            solution_name: The name of the solution file.

        Returns:
            str: The extension of the solution file.
        """
        _, ext = os.path.splitext(self.__solution_name)
        return ext.replace('.', '')

    def get_binary_file_path(self) -> str:
        """
        Returns the path to the binary file generated from the solution.

        Returns:
            str: The path to the binary file generated from the solution.
        """
        return os.path.join(Paths().get_problem_dir, 'bin', self.get_binary_name())

    def __generate_output_folder(self) -> str:
        """
        Returns the path to the folder where the output files generated by the solution are stored.

        Returns:
            str: The path to the folder where the output files generated by the solution are stored.
        """
        root_tmp_path: str = Paths().get_tmp_output_dir()
        output_folder: str = os.path.join(
            root_tmp_path, self.get_file_extension(), self.get_binary_name())
        return output_folder


class Test:
    """
    Represents a test case for an algorithm.

    Attributes:
        test_case: The input test case.
        exec_time: The execution time of the algorithm in seconds.
        memory_usage: The memory usage of the algorithm in bytes.
        status: The status of the test (e.g. PASSED, FAILED, TIMED_OUT).
        checker_output: The output of the checker (if applicable) for this test case.

    """

    def __init__(self, test_case: str, exec_time: float, memory_usage: int, status: Status, checker_output: str = ''):
        """
        Initializes a new instance of the Test class.

        Args:
            test_case (str): The input test case.
            exec_time (float): The execution time of the algorithm in seconds.
            memory_usage (int): The memory usage of the algorithm in bytes.

        """
        self.__test_case = test_case
        self.__exec_time = exec_time
        self.__memory_usage = memory_usage
        self.__status = status
        self.__checker_output = checker_output

    @property
    def test_case(self) -> str:
        """
        Get the input test case.

        Returns:
            The input test case.
        """
        return self.__test_case

    @property
    def exec_time(self) -> float:
        """
        Get the execution time of the algorithm in seconds.

        Returns:
            float: The execution time of the algorithm in seconds.
        """
        return self.__exec_time

    @property
    def memory_usage(self) -> float:
        """
        Get the memory usage of the algorithm in bytes.

        Returns:
            int: The memory usage of the algorithm in bytes.
        """
        return self.__memory_usage

    @property
    def status(self) -> Status:
        """
        Get the status of the test.

        Returns:
            Status: The status of the test.
        """
        return self.__status

    @property
    def checker_output(self) -> str:
        """
        Get the output of the checker.

        Returns:
            str: The output of the checker.
        """
        return self.__checker_output


@dataclass
class Statistic:
    """
    Represents a statistical summary of a solution.

    Attributes:
        ac_count: The count of accepted tests statuses.
        max_exec_time: The maximum execution time of a solution.
        max_memory_usage: The maximum memory usage of a solution.
    """
    ac_count: int
    max_exec_time: float
    max_memory_usage: float


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
