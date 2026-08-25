
from abc import ABC, abstractmethod
import io

class LatexFormatter(ABC):
    @abstractmethod
    def write_header(self, f_out: io.TextIOWrapper, problem_metadata: dict, options: dict) -> None:
        pass

    @abstractmethod
    def write_statement(self, f_out: io.TextIOWrapper, statement_lines: list) -> None:
        pass

    @abstractmethod
    def write_io_formats(self, f_out: io.TextIOWrapper, input_lines: list, output_lines: list, interactive: bool, interactor_lines: list) -> None:
        pass

    @abstractmethod
    def write_examples(self, f_out: io.TextIOWrapper, in_list: list, out_list: list) -> None:
        pass

    @abstractmethod
    def write_notes(self, f_out: io.TextIOWrapper, note_lines: list) -> None:
        pass

    @abstractmethod
    def write_footer(self, f_out: io.TextIOWrapper, options: dict) -> None:
        pass

    @abstractmethod
    def get_required_assets(self) -> list:
        pass

    def _print_line(self, line: str, f_out: io.TextIOWrapper) -> None:
        print(line, file=f_out, end='')