import io
import re

from ds_contest_tools.core.contracts.latex_formatter_interface import LatexFormatter
from ds_contest_tools.logger import info_log


class PolygonFormatter(LatexFormatter):
    """Generate statements using the Polygon-compatible LaTeX class."""

    def write_header(
        self, f_out: io.TextIOWrapper, problem_metadata: dict, options: dict
    ) -> None:
        print('\\documentclass{polygon}', file=f_out)
        print('\\begin{document}', file=f_out)
        if options.get('display_author'):
            print(
                '\\begin{ProblemaAutor}{' + options.get('problem_label', '')
                + '}{' + problem_metadata['problem']['title'] + '}{'
                + str(problem_metadata['problem']['time_limit']) + '}{'
                + str(problem_metadata['problem']['memory_limit_mb']) + '}{'
                + problem_metadata['author']['name'] + '}\n',
                file=f_out,
            )
        else:
            print(
                '\\begin{Problema}{' + options.get('problem_label', '')
                + '}{' + problem_metadata['problem']['title'] + '}{'
                + str(problem_metadata['problem']['time_limit']) + '}{'
                + str(problem_metadata['problem']['memory_limit_mb']) + '}\n',
                file=f_out,
            )

    def write_statement(
        self, f_out: io.TextIOWrapper, statement_lines: list
    ) -> None:
        if statement_lines:
            statement_lines[-1] = statement_lines[-1].rstrip()
            for line in statement_lines:
                self._print_line(line, f_out)

    def write_io_formats(
        self,
        f_out: io.TextIOWrapper,
        input_lines: list,
        output_lines: list,
        interactive: bool,
        interactor_lines: list,
    ) -> None:
        sections = (
            ('Entrada', input_lines),
            ('Saida', output_lines),
            ('Interacao', interactor_lines if interactive else []),
        )
        for command, lines in sections:
            if lines:
                print(f'\n\n\\{command}\n', file=f_out)
                lines[-1] = lines[-1].rstrip()
                for line in lines:
                    self._print_line(line, f_out)

    def write_examples(
        self, f_out: io.TextIOWrapper, in_list: list, out_list: list
    ) -> None:
        patterns = {
            '#': '\\#', '$': '\\$', '%': '\\%', '&': '\\&',
            '_': '\\_', '{': '\\{', '}': '\\}',
            '>': '\\textgreater{}', '<': '\\textless{}',
            '^': '\\textasciicircum{}', '\\': '\\textbackslash{}',
            ' ': '~',
        }
        regex = re.compile("(%s)" % '|'.join(map(re.escape, patterns)))

        def escape(text: str) -> str:
            return regex.sub(lambda match: patterns[match.group(0)], text)

        heading = '\\Examples' if len(in_list) > 1 else '\\Example'
        print(f'\n\n{heading}', file=f_out)
        print('\\begin{Exemplo}', file=f_out)
        for input_lines, output_lines in zip(in_list, out_list):
            max_lines = max(len(input_lines), len(output_lines))
            for line_index in range(max_lines):
                if line_index < len(input_lines):
                    print(
                        '\\texttt{' + escape(input_lines[line_index]) + '}',
                        end='',
                        file=f_out,
                    )
                print(' & ', end='', file=f_out)
                if line_index < len(output_lines):
                    print(
                        '\\texttt{' + escape(output_lines[line_index]) + '}',
                        end='',
                        file=f_out,
                    )
                print('\\\\', file=f_out)
            print('\\hline', file=f_out)
        print('\\end{Exemplo}\n', file=f_out)

    def write_notes(
        self, f_out: io.TextIOWrapper, note_lines: list
    ) -> None:
        if note_lines:
            print('\\Notas\n', file=f_out)
            for line in note_lines:
                self._print_line(line, f_out)

    def write_footer(
        self, f_out: io.TextIOWrapper, options: dict
    ) -> None:
        if options.get('display_author'):
            print('\\end{ProblemaAutor}', file=f_out)
        else:
            print('\\end{Problema}', file=f_out)
        print('\\end{document}', file=f_out)

    def get_required_assets(self) -> list:
        return ['polygon.cls', 'olymp.sty']
