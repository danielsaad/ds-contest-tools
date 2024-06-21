import os

DEFAULT_PDF_OPTIONS = {
    'display_author': True,
    'problem_label': '',
    'event': False
}

IGNORED_DIRS = [
    'boca', 'assets'
]

""" Java definitions """
JAVA_INTERPRETER = 'java'
JAVA_FLAG = '-classpath'
JAVA_VM_TEST_FILE = 'VmMemoryTest'
JAVA_VM_MEMORY_TEST_FOLDER = os.path.join(
    os.path.dirname(__file__), 'files/assets')

""" Python3 definitions """
PYTHON3_INTERPRETER = 'python3'
PYTHON_VM_MEMORY_TEST_FILE_PATH = os.path.join(
    os.path.dirname(__file__), 'files/assets/vm_memory_test.py')


def custom_key(str: str) -> tuple:
    """Sorts a string by its length and lexicographical order.

    Args:
        str: A string to be sorted.

    Returns:
        A tuple consisting of the length of the string and the string in lowercase.
    """
    return +len(str), str.lower()
