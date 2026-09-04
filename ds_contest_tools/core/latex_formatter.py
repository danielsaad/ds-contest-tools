import os
import re

from io import TextIOWrapper

from ds_contest_tools import config
from ds_contest_tools.enumarate.statement_files import StatementFiles


class LatexFormatter:
    """Serializa os metadados e a estrutura de um problema em LaTeX.

    É o **único** formatador do sistema. Não existe hierarquia de estratégias
    por formato porque não há comportamento divergente a encapsular: todos os
    formatos suportados recebem a mesma marcação, e a diferença visual entre
    eles vive inteiramente nas macros de cada `.cls`.

    Escreve em um arquivo já aberto. Não abre arquivos, não invoca `pdflatex`,
    não lê `problem.json` e não conhece `Paths()`.
    """

    def __init__(self, f_out: TextIOWrapper, problem_metadata: dict, options: dict, statement_folder: str) -> None:
        self.f_out = f_out
        self.problem_metadata = problem_metadata
        self.options = options
        self.statement_folder = statement_folder

    def __write_preamble(self) -> None:
        """Abre o documento com a classe escolhida pelo formato."""
        latex_class = self.options.get('latex_class', config.DEFAULT_LATEX_CLASS)
        class_name = os.path.splitext(
            config.LATEX_FORMATS[latex_class]['class_file'])[0]

        self.f_out.write(f"\\documentclass{{{class_name}}}")
        self.f_out.write("\\begin{document}")

    def write_header(self, ) -> None:
        self.__write_preamble()

        if self.options.get('event'):
            self.f_out.write(
                "\\Evento{" + self.problem_metadata['problem']['event'] + "}\n")

        if self.options.get('display_author'):
            self.f_out.write("\\begin{ProblemaAutor}{" + self.options.get('problem_label', '')
                  + "}{" + self.problem_metadata["problem"]["title"] + "}{" +
                  str(self.problem_metadata["problem"]["time_limit"]) +
                  "}{" +
                  str(self.problem_metadata["problem"]["memory_limit_mb"]) +
                  "}{" + self.problem_metadata["author"]["name"] + "}\n")
        else:
            self.f_out.write("\\begin{Problema}{" + self.options.get('problem_label', '')
                  + "}{" + self.problem_metadata["problem"]["title"] + "}{" +
                  str(self.problem_metadata["problem"]["time_limit"]) +
                  "}{" +
                  str(self.problem_metadata["problem"]["memory_limit_mb"]) +
                  "}\n")

    def write_description(self) -> None:
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.DESCRIPTION.file_name)
        self.f_out.write(latex_command)

    def write_input(self) -> None:
        self.f_out.write("\\Entrada\n\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.INPUT.file_name)
        self.f_out.write(latex_command)

    def write_output(self) -> None:
        self.f_out.write("\n\n\\Saida\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.OUTPUT.file_name)
        self.f_out.write(latex_command)

    def write_interactor(self) -> None:
        self.f_out.write("\n\n\\Interacao\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.INTERACTOR.file_name)
        self.f_out.write(latex_command)

    # def write_examples(self) -> None:
    #     pass

    def write_notes(self) -> None:
        self.f_out.write("\\Notas\n\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.NOTES.file_name)
        self.f_out.write(latex_command)

    def write_footer(self) -> None:
        if self.options.get('display_author'):
            self.f_out.write("\\end{ProblemaAutor}\n\n")
        else:
            self.f_out.write("\\end{Problema}\n\n")

        self.f_out.write("\\end{document}")

    def write_examples(self, in_list: list, out_list: list) -> None:
        patterns = {"#": "\\#", "$": "\\$", "%": "\\%", "&": "\\&", "_": "\\_",
                    "{": "\\{", "}": "\\}", ">": "\\textgreater{}", "<": "\\textless{}",
                    "^": "\\textasciicircum{}", "\\": "\\textbackslash{}", " ": "~"}

        def multiple_replace(patterns_dict, text):
            regex = re.compile("(%s)" % "|".join(
                map(re.escape, patterns_dict.keys())))
            return regex.sub(lambda mo: patterns_dict[mo.string[mo.start():mo.end()]], text)

        # Apenas a estrutura lógica é emitida aqui. Fonte, zebrado e
        # alinhamento são responsabilidade da classe LaTeX (\LinhaExemplo).
        self.f_out.write("\n\n\\ExemploEntrada\n")
        self.f_out.write("\\begin{Exemplo}")
        for tc in range(0, len(in_list)):
            tc_input = in_list[tc]
            tc_output = out_list[tc]
            self.f_out.write('\\CasoExemplo\n')
            max_lines = max(len(tc_input), len(tc_output))
            for i in range(0, max_lines):
                left = multiple_replace(
                    patterns, tc_input[i]) if i < len(tc_input) else ''
                right = multiple_replace(
                    patterns, tc_output[i]) if i < len(tc_output) else ''
                self.f_out.write(f'\\LinhaExemplo{{{left}}}{{{right}}}\n')
        self.f_out.write("\\end{Exemplo}\n\n")

    def write_tutorial(self) -> None:
        """Escreve o documento do tutorial (editorial) do problema.

        Emite apenas estrutura. Corpo da fonte, pacotes, numeração de página e
        layout do título são decididos pelo ambiente `Tutorial` de cada `.cls`
        — antes viviam num preâmbulo montado aqui em Python.
        """
        self.__write_preamble()

        self.f_out.write(
            "\\begin{Tutorial}{" + self.problem_metadata["problem"]["title"]
            + "}{" + self.problem_metadata["author"]["name"] + "}\n")

        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.TUTORIAL.file_name)
        self.f_out.write(latex_command)

        self.f_out.write("\\end{Tutorial}\n")
        self.f_out.write("\\end{document}")

    def __get_latex_input(self, statement_folder: str, file_name: str) -> str:
        """Write the LaTeX input command for the statement folder."""

        relative_path = self.__get_relative_path(statement_folder)
        latex_input = f"\\input{{{relative_path}/{file_name}}}"

        return latex_input + '\n\n'

    def __get_relative_path(self, statement_folder: str) -> str:
        """Return the relative path from base_path to target_path."""
        base_path: str = os.path.dirname(statement_folder)
        return os.path.relpath(statement_folder, base_path)
