#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argparse
from sys import argv
from argparse import ArgumentParser
from .parsers import build, clean, contest, convert, init, set_keys
from ds_contest_tools.parsers import helper_options


def add_argcomplete(parser: ArgumentParser):
    """Add autocomplete to the parser.

    Args:
        parser: The parser object.

    Returns:
        The parser object.
    """
    try:
        import subprocess

        import argcomplete
        command = ["eval", '"$(register-python-argcomplete)"', __file__]
        subprocess.run(command, shell=True)
        argcomplete.autocomplete(parser)
    except:
        pass


def create_parser() -> ArgumentParser:
    """Create a CLI parser of the tool.

    Returns:
        The parser object.
    """
    parser: ArgumentParser = ArgumentParser(
        prog="ds-contest-tools",
        formatter_class=argparse.RawTextHelpFormatter
        )

    helper_options.add_version_parser(parser)
    
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
    parser: ArgumentParser = create_parser()
    
    if len(argv) == 1:
        helper_options.print_welcome_message()
        parser.print_help()
        return

    options = parser.parse_args(argv[1:])
    options.function(options)


if __name__ == '__main__':
    main()
