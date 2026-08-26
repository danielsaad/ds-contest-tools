import io
import os
import re

from ds_contest_tools import config
from ds_contest_tools.core.contracts.latex_formatter_interface import LatexFormatter


class DsContestToolsFormatter(LatexFormatter):
    def write_header(self, f_out: io.TextIOWrapper, problem_metadata: dict, options: dict) -> None:
        latex_class = options.get('latex_class', config.DEFAULT_LATEX_CLASS)
        class_name = os.path.splitext(
            config.LATEX_FORMATS[latex_class]['class_file'])[0]
        print(f"\\documentclass{{{class_name}}}", file=f_out)
        print("\\begin{document}", file=f_out)
        if options.get('event'):
            print("\\lhead{" + problem_metadata['problem']['event'] + "}\n", file=f_out)
        
        if options.get('display_author'):
            print("\\begin{ProblemaAutor}{" + options.get('problem_label', '')
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}{" +
                  str(problem_metadata["problem"]["memory_limit_mb"]) +
                  "}{" + problem_metadata["author"]["name"] + "}\n", file=f_out)
        else:
            print("\\begin{Problema}{" + options.get('problem_label', '')
                  + "}{" + problem_metadata["problem"]["title"] + "}{" +
                  str(problem_metadata["problem"]["time_limit"]) +
                  "}{" +
                  str(problem_metadata["problem"]["memory_limit_mb"]) +
                  "}\n", file=f_out)

    def write_statement(self, f_out: io.TextIOWrapper, statement_lines: list) -> None:
        if statement_lines:
            statement_lines[-1] = statement_lines[-1].rstrip()
            for line in statement_lines:
                self._print_line(line, f_out)

    def write_io_formats(self, f_out: io.TextIOWrapper, input_lines: list, output_lines: list, interactive: bool, interactor_lines: list) -> None:
        if input_lines:
            print("\n\n\\Entrada\n", file=f_out)
            input_lines[-1] = input_lines[-1].rstrip()
            for line in input_lines:
                self._print_line(line, f_out)
        if output_lines:
            print("\n\n\\Saida\n", file=f_out)
            output_lines[-1] = output_lines[-1].rstrip()
            for line in output_lines:
                self._print_line(line, f_out)
        if interactive and interactor_lines:
            print("\n\n\\Interacao\n", file=f_out)
            for line in interactor_lines:
                self._print_line(line, f_out)

    def write_examples(self, f_out: io.TextIOWrapper, in_list: list, out_list: list) -> None:
        patterns = {"#": "\\#", "$": "\\$", "%": "\\%", "&": "\\&", "_": "\\_",
                    "{": "\\{", "}": "\\}", ">": "\\textgreater{}", "<": "\\textless{}",
                    "^": "\\textasciicircum{}", "\\": "\\textbackslash{}", " ": "~"}
        
        def multiple_replace(patterns_dict, text):
            regex = re.compile("(%s)" % "|".join(map(re.escape, patterns_dict.keys())))
            return regex.sub(lambda mo: patterns_dict[mo.string[mo.start():mo.end()]], text)

        print("\n\n\\ExemploEntrada", file=f_out)
        print("\\begin{Exemplo}", file=f_out)
        for tc in range(0, len(in_list)):
            tc_input = in_list[tc]
            tc_output = out_list[tc]
            max_lines = max(len(tc_input), len(tc_output))
            for i in range(0, max_lines):
                if tc % 2:
                    print('\\rowcolor{gray!20}', end='', file=f_out)
                if i < len(tc_input):
                    print('\\texttt{'+multiple_replace(patterns, tc_input[i])+'}', end='', file=f_out)
                print(' & ', end='', file=f_out)
                if i < len(tc_output):
                    print('\\texttt{'+multiple_replace(patterns, tc_output[i])+'}', end='', file=f_out)
                print('\\\\', file=f_out)
        print("\\end{Exemplo}\n", file=f_out)

    def write_notes(self, f_out: io.TextIOWrapper, note_lines: list) -> None:
        if note_lines:
            print("\\Notas\n", file=f_out)
            for line in note_lines:
                self._print_line(line, f_out)

    def write_footer(self, f_out: io.TextIOWrapper, options: dict) -> None:
        if options.get('display_author'):
            print("\\end{ProblemaAutor}", file=f_out)
        else:
            print("\\end{Problema}", file=f_out)
        print("\\end{document}", file=f_out)

    def get_required_assets(self) -> list:
        format_info = config.LATEX_FORMATS['ds-contest-tools']
        return [format_info['class_file'], *format_info.get('support_files', [])]
    