import argparse
import io
import json
import os
import shutil

from jsonutils import parse_json
from logger import info_log
from metadata import Paths
from utils import instance_paths, verify_path


def create_parser() -> argparse.ArgumentParser:
    """Create parser of the tool.

    Returns:
        argparse.ArgumentParser: The parser of the tool.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Convert legacy problems to newer version.")
    parser.add_argument('problem_dir', help='Path to the problem.')
    return parser


def write_file(statement_file: str, statement: io.TextIOWrapper) -> str:
    """Write a new file with a header from statement.

    Args:
        statement_file (str): Path to the new file.
        statement (io.TextIOWrapper): Stream to the statement.md

    Returns:
        str: The next header of the statement file.
    """
    text = ''
    with open(statement_file, 'w') as f:
        while (True):
            line = statement.readline()
            if not line or line.startswith('# '):
                f.write(text.lstrip().rstrip())
                return line
            text += line


def convert_statement() -> None:
    """Create statement directory and its files."""
    problem_path = Paths().get_problem_dir()
    if not os.path.join(problem_path, 'statement.md'):
        return

    info_log('Converting statement.md to TeX files.')
    statement_dir = os.path.join(problem_path, 'statement')
    statement_path = os.path.join(problem_path, 'statement.md')
    os.makedirs(statement_dir, exist_ok=True)

    with open(statement_path, 'r') as statement:
        statement.readline()

        files = {
            'description': 'description',
            'input': 'input',
            'output': 'output',
            'notes': 'notes',
            'tutorial': 'tutorial'
        }

        for _, prefix in files.items():
            file_path = os.path.join(statement_dir, f'{prefix}.tex')
            line = write_file(file_path, statement)
            if line.startswith('# Interação'):
                write_file(os.path.join(statement_dir,
                                        'interactor.tex'), statement)


def move_makefile() -> None:
    """Change CMake to Makefile"""
    problem_dir = Paths().get_problem_dir()
    tool_folder = os.path.dirname(os.path.abspath(__file__))

    info_log('Creating Makefile')
    cmake_path = os.path.join(problem_dir, 'CMakeLists.txt')
    if os.path.exists(cmake_path):
        os.remove(cmake_path)
    shutil.copy2(os.path.join(tool_folder, 'files', 'Makefile'), problem_dir)


def update_testlib() -> None:
    """Move updated testlib to src folder and remove the old one."""
    problem_dir = Paths().get_problem_dir()
    tool_folder = os.path.dirname(os.path.abspath(__file__))
    testlib_path = os.path.join(problem_dir, 'include', 'testlib.h')

    if os.path.exists(testlib_path):
        shutil.move(testlib_path, os.path.join(problem_dir, 'src'))
        os.rmdir(os.path.dirname(testlib_path))

    info_log('Moving testlib.h')
    shutil.copy2(os.path.join(tool_folder, 'files', 'src', 'testlib.h'),
                 os.path.join(problem_dir, 'src', 'testlib.h'))


def convert_problem_json() -> None:
    """Convert problem.json to new version."""
    problem_dir = Paths().get_problem_dir()
    tool_folder = os.path.dirname(os.path.abspath(__file__))

    metadata_path = os.path.join(problem_dir, 'problem.json')
    if not os.path.exists(metadata_path):
        return

    info_log('Converting problem.json')
    old_problem_metadata = parse_json(metadata_path)
    shutil.copy2(os.path.join(tool_folder, 'files',
                 'problem.json'), metadata_path)
    new_problem_metadata = parse_json(metadata_path)

    for key, value in old_problem_metadata.items():
        if key == 'io_samples':
            new_problem_metadata[key] = value
            continue
        
        for subkey, subvalue in value.items():
            new_problem_metadata[key][subkey] = subvalue

    del new_problem_metadata['problem']['id']
    del new_problem_metadata['problem']['label']

    with open(metadata_path, 'w') as f:
        f.write(json.dumps(new_problem_metadata, ensure_ascii=False))


def convert_problem() -> None:
    """Convert legacy problem to newer version."""
    move_makefile()
    update_testlib()
    convert_statement()
    convert_problem_json()


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    verify_path(args.problem_dir)
    instance_paths(args.problem_dir)

    convert_problem()

    print('Update the solutions in problem.json file.')
    print('Problem converted successfully.')
