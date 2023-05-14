import argparse
from sys import argv

from .parsers import build, clean, contest, convert, gen, init, set_keys


def create_parser() -> argparse.ArgumentParser:
    """Create parser for ds-contest-tools

    Returns:
        The parser object.
    """
    parser = argparse.ArgumentParser(prog="ds-contest-tools")
    subparsers = parser.add_subparsers(
        title='available commands',
        description='',
        help='DESCRIPTION',
        metavar="COMMAND",
        required=True
    )
    init.add_parser(subparsers)
    build.add_parser(subparsers)
    gen.add_parser(subparsers)
    contest.add_parser(subparsers)
    convert.add_parser(subparsers)
    set_keys.add_parser(subparsers)
    clean.add_parser(subparsers)
    return parser


def main():
    parser = create_parser()
    options = parser.parse_args(argv[1:])
    options.function(options)


if __name__ == '__main__':
    main()
