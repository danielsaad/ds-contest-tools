import argparse
import os
import sys


def create_parser() -> argparse.ArgumentParser:
    """Create argparser for the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('problem_dir', help='Path to the problem.')
    return parser


def write_file(statement_file: str, statement) -> str:
    """Write a new statement file."""
    text = ''
    with open(statement_file, 'w') as f:
        while (True):
            line = statement.readline()
            if (not line or line.startswith('# ')):
                f.write(text.lstrip().rstrip())
                return line
            text += line


def convert_statement(problem_path: str) -> None:
    """Create statement directory and its files."""
    statement_dir = os.path.join(problem_path, 'statement')
    os.makedirs(statement_dir, exist_ok=True)
    statement_path = os.path.join(problem_path, 'statement.md')
    with open(statement_path, 'r') as statement:
        statement.readline()
        write_file(os.path.join(statement_dir, 'description.tex'), statement)
        write_file(os.path.join(statement_dir, 'input.tex'), statement)
        line = write_file(os.path.join(statement_dir, 'output.tex'), statement)
        if (line.startswith('# Interação')):
            write_file(os.path.join(statement_dir,
                       'interactor.tex'), statement)
        write_file(os.path.join(statement_dir, 'notes.tex'), statement)
        write_file(os.path.join(statement_dir, 'tutorial.tex'), statement)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not os.path.exists():
        print("Path does not exist.")
        sys.exit(0)
    if not os.path.join(args.problem_dir, 'statement.md'):
        print("Statement file does not exist.")
        sys.exit(0)

    convert_statement(args.problem_dir)
    print('statement.md converted successfully.')
