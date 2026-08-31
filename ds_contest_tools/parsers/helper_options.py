from argparse import ArgumentParser
from ds_contest_tools import __version__

def add_version_parser(parser: ArgumentParser) -> None:
    """
    Add a option for tag version

    Args:
        parsers: The argparse parser object.
    """
    version_text: str = (
        f"Welcome to ds-contest-tools!\n"
        f"Version {__version__}\n"
        f"Website: https://danielsaad.com/ds-contest-tools/"
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=version_text,
        help="show program's version."
    )

def print_welcome_message() -> None:
    """Print the welcome message (used when no arguments are provided)."""
    print(
        f"Welcome to ds-contest-tools!\n"
        f"Version {__version__}\n"
        f"Website: https://danielsaad.com/ds-contest-tools/\n"
    )
