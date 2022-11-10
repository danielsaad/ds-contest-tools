DEFAULT_PDF_OPTIONS = {
    'display_author': True,
    'problem_label': ''
}


def custom_key(str: str) -> str:
    """Sorting function. Firstly sort by lenght and 
    secondly by lexicographical order.
    """
    return +len(str), str.lower()
