import os
import re

from io import TextIOWrapper

from ds_contest_tools import config
from ds_contest_tools.enumarate.statement_files import StatementFiles
from ds_contest_tools.util.jsonutils import parse_json
from ds_contest_tools.util.latexutils import get_io
from ds_contest_tools.logger import error_log, info_log
from ds_contest_tools.util.utils import check_problem_metadata, verify_path
from ds_contest_tools.util.fileutils import has_lines


class LatexFormatter:
    """Serializa os metadados e a estrutura de um problema em LaTeX.

    É o **único** formatador do sistema. Não existe hierarquia de estratégias
    por formato porque não há comportamento divergente a encapsular: todos os
    formatos suportados recebem a mesma marcação, e a diferença visual entre
    eles vive inteiramente nas macros de cada `.cls`.

    Escreve em um arquivo já aberto. Não abre arquivos, não invoca `pdflatex`,
    não lê `problem.json` e não conhece `Paths()`.
    """

    def __init__(self, options: dict, problem_folder: str) -> None:
        self.f_out: TextIOWrapper = None
        self.options = options
        self.problem_folder = problem_folder
        self.statement_folder: str = ''
        self.problem_metadata: dict = {}

        self.__set_problem_statement_folder()
        self.__set_problem_metadata()
        

    def write_latex_file(self) -> None:
        """Escreve o arquivo LaTeX do problema, incluindo preâmbulo, enunciado,
        exemplos e notas.

        O arquivo é escrito no mesmo diretório do enunciado, com o nome
        `problem.tex`. O conteúdo do arquivo é determinado pelo dicionário
        `problem_metadata` e pelas opções de formatação em `options`.
        """
        tex_filename = os.path.basename(os.path.abspath(self.problem_folder)) + '.tex'
        tex_filepath = os.path.join(self.problem_folder, tex_filename)
        info_log(f"Creating {os.path.basename(tex_filepath)}")

        with open(tex_filepath, 'w') as f_out:
            self.f_out: TextIOWrapper = f_out
            self.__write_header()
            self.__write_description()
            self.__write_input()
            self.__write_output()

            interactive: bool = self.problem_metadata['problem']['interactive']
            if interactive:
                self.__write_interactor()

            self.__write_examples()
            self.__write_notes()
            self.__write_footer()

        if has_lines(self.statement_folder, StatementFiles.TUTORIAL):
            tutorial_filename = os.path.basename(
                os.path.abspath(self.problem_folder)) + '-tutorial.tex'
            tutorial_filepath = os.path.join(self.problem_folder, tutorial_filename)
            info_log(f"Creating {tutorial_filename}")
        
            with open(tutorial_filepath, 'w') as f_out:
                self.f_out: TextIOWrapper = f_out
                self.__write_tutorial()

    def __write_preamble(self, pagination_option: str) -> None:
        """Abre o documento com a classe escolhida pelo formato.

        Args:
            pagination_option: Chave de `options` com a paginação deste
                documento no caderno (`pagination` ou `tutorial_pagination`).
        """
        latex_class = self.options.get('latex_class', config.DEFAULT_LATEX_CLASS)
        class_name = os.path.splitext(
            config.LATEX_FORMATS[latex_class]['class_file'])[0]

        self.f_out.write(f"\\documentclass{{{class_name}}}")
        self.f_out.write("\\begin{document}")

        if self.options.get('page_numbers'):
            self.f_out.write("\\NumerarPaginas\n")

        pagination = self.options.get(pagination_option)
        if pagination:
            first_page, total_pages = pagination
            self.f_out.write(f"\\Paginacao{{{first_page}}}{{{total_pages}}}\n")

    def __write_header(self, ) -> None:
        self.__write_preamble('pagination')

        if self.options.get('event'):
            self.f_out.write(
                "\\Evento{" + self.problem_metadata['problem']['event'] + "}\n")

        problem = self.problem_metadata["problem"]
        if self.options.get('display_limits', True):
            time_limit = str(problem.get("time_limit", ''))
            memory_limit = str(problem.get("memory_limit_mb", ''))
        else:
            time_limit = memory_limit = ''

        header_args = ("{" + self.options.get('problem_label', '') + "}{" + problem["title"]
                       + "}{" + time_limit + "}{" + memory_limit + "}")

        if self.options.get('display_author'):
            self.f_out.write("\\begin{ProblemaAutor}" + header_args
                             + "{" + self.problem_metadata["author"]["name"] + "}\n")
        else:
            self.f_out.write("\\begin{Problema}" + header_args + "\n")

    def __write_description(self) -> None:
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.DESCRIPTION.file_name)
        self.f_out.write(latex_command)

    def __write_input(self) -> None:
        self.f_out.write("\\Entrada\n\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.INPUT.file_name)
        self.f_out.write(latex_command)

    def __write_output(self) -> None:
        self.f_out.write("\n\n\\Saida\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.OUTPUT.file_name)
        self.f_out.write(latex_command)

    def __write_interactor(self) -> None:
        self.f_out.write("\n\n\\Interacao\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.INTERACTOR.file_name)
        self.f_out.write(latex_command)

    def __write_notes(self) -> None:
        if not has_lines(self.statement_folder, StatementFiles.NOTES):
            return
        self.f_out.write("\\Notas\n\n")
        latex_command: str = self.__get_latex_input(
            self.statement_folder, StatementFiles.NOTES.file_name)
        self.f_out.write(latex_command)

    def __write_footer(self) -> None:
        if self.options.get('display_author'):
            self.f_out.write("\\end{ProblemaAutor}\n\n")
        else:
            self.f_out.write("\\end{Problema}\n\n")

        self.f_out.write("\\end{document}")

    def __write_examples(self) -> None:
        input_folder: str = os.path.join(self.problem_folder, 'input')
        output_folder: str = os.path.join(self.problem_folder, 'output')

        in_list = get_io(input_folder, self.problem_metadata)
        out_list = get_io(output_folder, self.problem_metadata)

        patterns = {"#": "\\#", "$": "\\$", "%": "\\%", "&": "\\&", "_": "\\_",
                    "{": "\\{", "}": "\\}", ">": "\\textgreater{}", "<": "\\textless{}",
                    "^": "\\textasciicircum{}", "\\": "\\textbackslash{}", " ": "~"}

        def multiple_replace(patterns_dict, text):
            regex = re.compile("(%s)" % "|".join(
                map(re.escape, patterns_dict.keys())))
            return regex.sub(lambda mo: patterns_dict[mo.string[mo.start():mo.end()]], text)

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

    def __write_tutorial(self) -> None:
        """Escreve o documento do tutorial (editorial) do problema.

        Emite apenas estrutura. Corpo da fonte, pacotes, numeração de página e
        layout do título são decididos pelo ambiente `Tutorial` de cada `.cls`
        — antes viviam num preâmbulo montado aqui em Python.
        """
        self.__write_preamble('tutorial_pagination')

        author = self.problem_metadata["author"]["name"] if self.options.get('display_author') else ''
        self.f_out.write(
            "\\begin{Tutorial}{" + self.problem_metadata["problem"]["title"]
            + "}{" + author + "}\n")

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


    def __set_problem_statement_folder(self) -> None:
        statement_folder = os.path.join(self.problem_folder, 'statement')
        verify_path(statement_folder)
        self.statement_folder = statement_folder

    def __set_problem_metadata(self) -> None:
        """Reads and validates the problem metadata from the problem.json file.

        Limits are optional here: when missing, the PDF does not show them.
        """
        problem_json_path = os.path.join(self.problem_folder, 'problem.json')
        problem_metadata = parse_json(problem_json_path)
        check_problem_metadata(problem_metadata, require_limits=False)
        if not problem_metadata['problem']['title'].strip():
            error_log("Variable 'title' in 'problem' is empty in problem.json.")
        self.problem_metadata = problem_metadata
