from ds_contest_tools.core.contracts.latex_formatter_interface import LatexFormatter
from ds_contest_tools.core.ds_contest_tools_formatter import DsContestToolsFormatter
from ds_contest_tools.core.polygon_formatter import PolygonFormatter


class FormatterFactory:
    @staticmethod
    def get_formatter(latex_class: str) -> LatexFormatter:
        formatters = {
            'polygon': PolygonFormatter,
            'ds-contest-tools': DsContestToolsFormatter,
        }
        try:
            return formatters[latex_class]()
        except KeyError as error:
            raise ValueError(f"Unknown LaTeX format: {latex_class}") from error