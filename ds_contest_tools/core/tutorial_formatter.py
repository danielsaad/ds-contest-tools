import io
import os
from ds_contest_tools.logger import info_log

class TutorialFormatter:
    def __init__(self, problem_metadata: dict):
        self.problem_metadata = problem_metadata

    def build_tutorial(self, problem_folder: str, tutorial_lines: list) -> None:
        """Generates the LaTeX file for the tutorial of a problem.

        Args:
            problem_folder: The path to the problem directory.
            tutorial_lines: A list of strings containing the tutorial lines.
        """
        tex_filepath = os.path.join(problem_folder, os.path.basename(
            os.path.abspath(problem_folder)) + '-tutorial.tex')
        info_log(f"Creating {os.path.basename(tex_filepath)}")
        with open(tex_filepath, 'w') as f_out:
            print("\\documentclass[10pt]{article}", file=f_out)
            print("\\usepackage[utf8]{inputenc}", file=f_out)
            print("\\usepackage{amsmath,amsthm,amssymb}", file=f_out)
            print("\\usepackage{fullpage}", file=f_out)
            print("\\usepackage{url}", file=f_out)
            print("\\pagenumbering{gobble}", file=f_out)
            print("\\title{ Tutorial: " +
                  self.problem_metadata["problem"]["title"]+"}", file=f_out)
            print("\\author{"+self.problem_metadata["author"]["name"]+"}", file=f_out)
            print("\\date{}", file=f_out)
            print("\\begin{document}", file=f_out)
            print("\\maketitle", file=f_out)
            for line in tutorial_lines:
                self._print_line(line, f_out)
            print("\\end{document}", file=f_out)

    def _print_line(self, line: str, f_out: io.TextIOWrapper) -> None:
        """Writes a line to a file.

        Args:
            line: The line to be written to the file.
            f_out: The file to which the line will be written.
        """
        print(line, file=f_out, end='')