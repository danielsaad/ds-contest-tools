import os
import shutil
from json import dumps
from math import log10, floor
from logger import info_log


def rename_io(io_folder: str) -> None:
    """Receives a list of files and adds leading zeros 
    to the name of each one.
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
    """Recursively creates folders to 'dest' path and
    copy files of 'src' to it."""
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
    """Copy a directory structure overwriting existing files"""
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


def write_secrets() -> None:
    """Write file to store sensitive information used by the tools."""
    info_log("Writing secrets file.")

    tool_path = os.path.dirname(os.path.abspath(__file__))
    secrets = {
        "apikey": "",
        "secret": "", }
    with open(os.path.join(tool_path, 'secrets.json'), 'w') as f:
        f.write(dumps(secrets))
