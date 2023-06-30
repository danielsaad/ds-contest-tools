DEFAULT_PDF_OPTIONS = {
    'display_author': True,
    'problem_label': '',
    'event': False
}

IGNORED_FILES = [
    'boca', 'assets'
]


def custom_key(str: str) -> tuple:
    """Sorts a string by its length and lexicographical order.

    Args:
        str: A string to be sorted.

    Returns:
        A tuple consisting of the length of the string and the string in lowercase.
    """
    return +len(str), str.lower()
