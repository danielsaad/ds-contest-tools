import argparse
import io
import os
import sys


def create_parser() -> argparse.ArgumentParser:
    """Create parser of the tool.

    Returns:
        argparse.ArgumentParser: The parser of the tool.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
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


def convert_statement(problem_path: str) -> None:
    """Create statement directory and its files.

    Args:
        problem_path (str): Path to the problem folder.
    """
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


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not os.path.exists(args.problem_dir):
        print("Problem folder does not exist.")
        sys.exit(0)
    if not os.path.exists(os.path.join(args.problem_dir, 'statement.md')):
        print("Statement file does not exist.")
        sys.exit(0)

    convert_statement(args.problem_dir)
    print('statement.md converted successfully.')
