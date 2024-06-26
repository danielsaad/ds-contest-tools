from typing import Union

from ..boca import boca_pack
from ..jsonutils import parse_json
from ..metadata import Paths
from ..polygon_converter import get_polygon_problem
from ..polygon_submitter import send_to_polygon
from ..sqtpm import convert_to_sqtpm
from .common import *


def verify_polygon_keys() -> None:
    """Check if the Polygon API keys file has been created and is accessible.

    The function checks whether the `secrets.json` file that contains the 
    Polygon API keys exists in the directory of this script.
    """
    tool_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(tool_path, 'secrets.json')

    if not os.path.exists(secrets_path):
        error_log("Keys are not defined. Use 'set_keys' to define it.")


def verify_problem_type(problem_format: str) -> None:
    """Check if the problem format is valid to convert.

    Args:
        problem_format: Format to convert the problem.
    """
    problem_json = os.path.join(Paths().get_problem_dir(), 'problem.json')
    problem_json = parse_json(problem_json)
    
    interactive = problem_json['problem']['interactive']
    no_interactive_formats = ['boca', 'sqtpm']
    if problem_format in no_interactive_formats and interactive:
        error_log(f'Interactive problems are not supported by {problem_format.upper()}.')
    
    grader = problem_json['problem']['grader']
    no_grader_formats = ['boca', 'sqtpm']
    if problem_format in no_grader_formats and grader:
        error_log(f'Grader problems are not supported by {problem_format.upper()}.')


def process_convert_to(problem_format: str, problem_dir: str, output_dir: Union[str, None], manual_testcases: bool) -> None:
    """Convert problem from DS to Polygon, SQTPM or BOCA.

    Args:
        problem_format: Format to convert the problem.
        problem_dir: Path to the problem directory.
        output_dir: Path the converted problem directory or ID of the Polygon 
        problem, if one is not defined yet.
    """
    if problem_format == 'polygon':
        setup_and_validate_paths(problem_dir)
        verify_problem_type(problem_format)
        verify_polygon_keys()
        send_to_polygon(output_dir, manual_testcases)
    elif problem_format == 'boca':
        if not output_dir:
            output_dir = problem_dir
        setup_and_validate_paths(problem_dir, output_dir)
        verify_problem_type(problem_format)
        boca_pack(Paths().get_problem_dir(), Paths().get_output_dir())
    elif problem_format == 'sqtpm':
        if not output_dir:
            output_dir = os.path.join(problem_dir, 'sqtpm')
        setup_and_validate_paths(problem_dir, output_dir)
        verify_problem_type(problem_format)
        convert_to_sqtpm()

    info_log('Problem converted successfully.')


def process_convert_from(problem_format: str, problem_dir: str, package_dir: str, local: bool) -> None:
    """Convert problem from some format to DS.

    Args:
        problem_format: Format to convert the problem.
        problem_dir: Path to the converted problem directory.
        package_dir: Path to the problem package or Polygon ID.
        local: Convert local polygon package. Use the package path instead of ID in package_dir.
    """
    if problem_format == 'polygon':
        if local:
            setup_and_validate_paths(problem_dir, package_dir, verify_path=False)
        else:
            setup_and_validate_paths(problem_dir, os.path.join(
                problem_dir, 'temp_polygon_package'), verify_path=False)
            verify_polygon_keys()
        get_polygon_problem(package_dir, local)
    else:
        error_log('Not implemented yet.')
    info_log('Problem converted successfully.')


def add_parser(subparsers) -> None:
    """
    Add a subparser for the 'convert_to' and 'convert_from' commands.

    Args:
        subparsers: The argparse subparsers object.
    """
    to_parser = subparsers.add_parser(
        'convert_to', help='convert problem to some format')
    to_parser.add_argument('format', choices=[
                           'boca', 'polygon', 'sqtpm'],
                           help='format to convert the problem')
    to_parser.add_argument(
        'problem_dir', help='path to the problem directory')
    to_parser.add_argument('-o', '--output_dir',
                           help='destination path to save the converted problem or '
                           'the id of the polygon problem if it has not yet been defined. '
                           'By default, the output directory is the same as the problem directory, '
                           'except for polygon problems, which are saved online')
    to_parser.add_argument('-m', '--manual_tests', action='store_true',
                           help='send testcases without the script')
    to_parser.set_defaults(function=lambda options: process_convert_to(
        options.format, options.problem_dir, options.output_dir, options.manual_tests))

    from_parser = subparsers.add_parser(
        'convert_from', help='convert problem to ds format')
    from_parser.add_argument(
        'format', choices=['polygon'], help='format to convert the problem')
    from_parser.add_argument(
        'problem_dir', help='path to the converted problem directory')
    from_parser.add_argument(
        'package_dir', help='path to the problem package or polygon id')
    from_parser.add_argument('-l', '--local', action='store_true',
                             help='convert local polygon package, use the package path '
                             'instead of the id in "package_dir" argument')
    from_parser.set_defaults(function=lambda options: process_convert_from(
        options.format, options.problem_dir, options.package_dir, options.local))
