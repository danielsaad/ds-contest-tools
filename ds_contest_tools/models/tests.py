from ds_contest_tools.enumarate.status import Status

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