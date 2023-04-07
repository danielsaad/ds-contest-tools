import os
import shutil
import sys
from math import floor, log10
from typing import Optional

from jsonutils import parse_json
from logger import error_log
from utils import verify_path


def rename_io(io_folder: str) -> None:
    """Renames files in the given directory by adding leading zeros to 
    the filenames for numerical sorting purposes.

    Args:
        io_folder: The path of the directory to rename files in.
    """
    if os.path.isdir(io_folder):
        files = os.listdir(io_folder)
        fcount = len(files)
        if (fcount == 0):
            return
        zeros = floor(log10(fcount)) + 1
        for f in files:
            src = os.path.join(io_folder, f)
            dst = os.path.join(io_folder, f.zfill(zeros))
            os.rename(src, dst)


def recursive_overwrite(src: str, dest: str, ignore=None) -> None:
    """Recursively creates folders to 'dest' path and copies files 
    from 'src' to 'dest'.

    Args:
        src: The path to the source file or directory.
        dest: The path to the destination directory.
        ignore: A function that takes two arguments: the directory being visited, 
                                     and a list of its contents, and returns a set of the files and/or 
                                     directories to ignore. Default is None.
    """
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)


def copy_directory(source: str, dest: str) -> None:
    """Recursively copies the directory structure and files 
    from the source directory to the destination directory,
    overwriting existing files.

    Args:
        source: The path to the source directory.
        dest: The path to the destination directory.
    """
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
            if (dirs and files):
                shutil.copyfile(os.path.join(root, file),
                                os.path.join(dest_path, file))


def get_statement_files(statement_folder: str, interactive: Optional[bool] = False) -> list:
    """Return list of statement files of the problem.

    Args:
        statement_folder: Path to the statement folder.
        interactive : Wheter the problem is interactive. Defaults to False.

    Returns:
        A list containing the absolute path to the statement files.
    """
    statement_files = ['description.tex',
                       'input.tex',
                       'output.tex',
                       'notes.tex',
                       'tutorial.tex']
    if interactive:
        statement_files.append('interactor.tex')

    statement_files = [os.path.join(statement_folder, file)
                       for file in statement_files]
    [verify_path(file) for file in statement_files]
    return statement_files


def check_interactive_problem(problem_dir: str) -> bool:
    """Checks whether the problem is interactive based on the metadata.

    Args:
        problem_dir: Path to the problem directory.

    Returns:
        True if the problem is interactive, False otherwise.
    """
    metadata_path = os.path.join(problem_dir, 'problem.json')
    verify_path(metadata_path)
    problem_metadata = parse_json(metadata_path)
    if 'problem' not in problem_metadata or 'interactive' not in problem_metadata['problem']:
        error_log("Interactive value in problem.json is not defined.")
        sys.exit(0)
    return problem_metadata['problem']['interactive']
