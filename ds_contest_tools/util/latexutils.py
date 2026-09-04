import os

from .utils import verify_path


def get_io(io_folder: str, problem_metadata: dict) -> list:
    """Return input/output examples for the problem from the given folder.

    Args:
        io_folder: The path to the directory containing the input/output files.
        problem_metadata: A dictionary containing metadata about the problem.

    Returns:
        A list of input/output examples to be used in the PDF.
    """
    l = []
    io_samples = problem_metadata["io_samples"]
    interactive = problem_metadata['problem']['interactive']

    if interactive:
        io_files = [os.path.join(io_folder, str(f)+'.interactive')
                    for f in range(1, io_samples+1)]
    else:
        io_files = [os.path.join(io_folder, str(f))
                    for f in range(1, io_samples+1)]

    for f in io_files:
        verify_path(f)
        tc_io = []
        with open(f) as inf:
            for line in inf.readlines():
                tc_io.append(line.rstrip('\n'))
        l.append(tc_io)
    return l


def clean_auxiliary_files(folder: str, extensions: list = None) -> None:
    """Remove files with specified extensions from a given directory.

    Args:
        folder: The directory to clean up.
        extensions: A list of file extensions to remove.
    """
    if extensions is None:
        extensions = ['.aux', '.log', '.out']

    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in extensions and f not in ['tool.log', 'debug.log']:
                os.remove(os.path.join(root, f))
