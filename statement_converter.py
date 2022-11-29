import argparse
import os
import sys
from utils import instance_paths
from metadata import Paths
from logger import info_log


def create_parser() -> argparse.ArgumentParser:
    """Create argparser for the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('problem_dir', help='Path to the problem.')
    return parser


def write_file(statement_file: str, statement) -> str:
    """Write a new file."""
    with open(statement_file, 'w') as f:
        while (True):
            line = statement.readline()
            if (not line or line.startswith('# ')):
                info_log(f'File {os.path.basename(f.name)} created.')
                return line
            f.write(line)


def convert_statement(statement_dir='') -> None:
    """Create statement directory and its files."""
    if statement_dir == '':
        statement_dir = os.path.join(
            Paths.instance().dirs['problem_dir'], 'statement')
    os.makedirs(statement_dir, exist_ok=True)

    statement_path = os.path.join(
        Paths.instance().dirs['problem_dir'], 'statement.md')
    with open(statement_path, 'r') as statement:
        statement.readline()
        write_file(os.path.join(statement_dir, 'descricao.tex'), statement)
        write_file(os.path.join(statement_dir, 'entrada.tex'), statement)
        line = write_file(os.path.join(statement_dir, 'saida.tex'), statement)
        if (line.startswith('# Interação')):
            write_file(os.path.join(statement_dir, 'interacao.tex'), statement)
        write_file(os.path.join(statement_dir, 'notas.tex'), statement)
        write_file(os.path.join(statement_dir, 'tutorial.tex'), statement)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if (not os.path.exists(args.problem_dir)):
        print("Path does not exist.")
        sys.exit(0)
    if (not os.path.join(args.problem_dir, 'statement.md')):
        print("Statement file does not exist.")
        sys.exit(0)
    instance_paths(args.problem_dir)

    convert_statement()
    print('statement.md converted successfully.')
