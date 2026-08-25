from dataclasses import dataclass


@dataclass
class BuildOptions:
    """
    Class to hold the build options for a problem.

    Attributes:
        all_solutions: Whether to build all solutions or not.
        specific_solution: Name of the solution to be checked.
        cpu_count: Number of threads to be used when checking solutions.
        io: Whether to generate only input/output files or not.
        pdf: Whether to generate only PDFs or not.
        no_validator: Whether to build problem without the validator or not.
        no_generator: Whether to build problem without the generator or not.
        no_checker: Whether to build problem without running the checker or not.
        no_output: Whether to build problem without generating output or not.
        ngvoc: Whether to build only problem executables and PDFs or not.
        latex_class: LaTeX class file to be used to build the PDFs.
        problem_dir: Path to the problem directory.
    """

    def __init__(self, problem_dir: str, all_solutions: bool, specific_solution: str, cpu_count: int, io: bool, pdf: bool, no_validator: bool, no_generator: bool, no_checker: bool, no_output: bool, ngvoc: bool, latex_class: str = 'ds-contest-tools'):
        self.problem_dir = problem_dir
        self.all_solutions = all_solutions
        self.specific_solution = specific_solution
        self.cpu_count = cpu_count
        self.io = io
        self.pdf = pdf
        self.no_validator = no_validator
        self.no_generator = no_generator
        self.no_checker = no_checker
        self.no_output = no_output
        self.ngvoc = ngvoc
        self.latex_class = latex_class