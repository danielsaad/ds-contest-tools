import os
import shutil


def rename_io(io_folder, zeros=4):
    """Receives a list of files and adds leading zeros 
    to the name of each one.
    """
    for filename in os.listdir(io_folder):
        src = os.path.join(io_folder, filename)
        dst = os.path.join(io_folder, filename.zfill(zeros))
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
            if(dirs and files):
                shutil.copyfile(os.path.join(root, file),
                                os.path.join(dest_path, file))
