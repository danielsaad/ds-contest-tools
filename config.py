DEFAULT_PDF_OPTIONS = {
    'display_author': True,
    'problem_label': ''
}

"""
Sorting function. Firstly Sort by lenght and secondly by lexicographical order.
"""
def custom_key(str):
    return +len(str), str.lower()
