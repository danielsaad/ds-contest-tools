import io
import os
from ds_contest_tools.enumarate.statement_files import StatementFiles
from ds_contest_tools.logger import info_log

class TutorialFormatter:
    def __init__(self, problem_metadata: dict, problem_folder: str) -> None:
        self.problem_folder: str = problem_folder
        self.problem_metadata = problem_metadata

    def build_tutorial(self) -> None:
        """Generates the LaTeX file for the tutorial of a problem.

        Args:
            tutorial_lines: A list of strings containing the tutorial lines.
        """
        tex_filepath = os.path.join(self.problem_folder, os.path.basename(
            os.path.abspath(self.problem_folder)) + '-tutorial.tex')
        info_log(f"Creating {os.path.basename(tex_filepath)}")
        with open(tex_filepath, 'w') as f_out:
            f_out.write("\\documentclass[10pt]{article}\n")
            f_out.write("\\usepackage[utf8]{inputenc}\n")
            f_out.write("\\usepackage{amsmath,amsthm,amssymb}\n")
            f_out.write("\\usepackage{fullpage}\n")
            f_out.write("\\usepackage{url}\n")
            f_out.write("\\pagenumbering{gobble}\n")
            f_out.write("\\title{ Tutorial: " +
                  self.problem_metadata["problem"]["title"]+"}\n")
            f_out.write("\\author{"+self.problem_metadata["author"]["name"]+"}\n")
            f_out.write("\\date{}\n")
            f_out.write("\\begin{document}\n")
            f_out.write("\\maketitle\n")

            latex_command: str = self.__get_latex_input(
                os.path.join(self.problem_folder, 'statement'), StatementFiles.TUTORIAL.file_name)
            f_out.write(latex_command)
            
            f_out.write("\\end{document}")

    def __get_latex_input(self, statement_folder: str, file_name: str) -> str:
            """Write the LaTeX input command for the statement folder."""
    
            relative_path = self.__get_relative_path(statement_folder)
            latex_input = f"\\input{{{relative_path}/{file_name}}}"
    
            return latex_input + '\n\n'
    
    def __get_relative_path(self, statement_folder: str) -> str:
        """Return the relative path from base_path to target_path."""
        base_path: str = os.path.dirname(statement_folder)
        return os.path.relpath(statement_folder, base_path)
