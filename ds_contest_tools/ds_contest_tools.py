#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argparse
from sys import argv

from .parsers import build, clean, contest, convert, init, set_keys


def add_argcomplete(parser: argparse.ArgumentParser):
    """Add autocomplete to the parser.

    Args:
        parser: The parser object.

    Returns:
        The parser object.
    """
    try:
        import argcomplete
        import subprocess
        command = ["eval", '"$(register-python-argcomplete)"', __file__]
        subprocess.run(command, shell=True)
        argcomplete.autocomplete(parser)
    except:
        pass


def create_parser() -> argparse.ArgumentParser:
    """Create a CLI parser of the tool.

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
    contest.add_parser(subparsers)
    convert.add_parser(subparsers)
    set_keys.add_parser(subparsers)
    clean.add_parser(subparsers)
    add_argcomplete(parser)
    return parser


def main():
    parser = create_parser()
    options = parser.parse_args(argv[1:])
    options.function(options)


if __name__ == '__main__':
    main()
