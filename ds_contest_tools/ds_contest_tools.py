import argparse
from sys import argv

from .parsers import init


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ds-contest-tools")
    subparsers = parser.add_subparsers(
        title='available commands',
        description='',
        help='DESCRIPTION',
        metavar="COMMAND",
        required=True
    )
    init.add_parser(subparsers)
    return parser


def main():
    parser = create_parser()
    options = parser.parse_args(argv[1:])
    options.function(options)


if __name__ == '__main__':
    main()
