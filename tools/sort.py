#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os import getcwd, mkdir, walk
from os.path import isdir, isfile, getmtime
from sys import argv
from datetime import datetime
from threading import Thread
from shutil import copyfile


def check_dir(path: str):
    """Make sur a directory exist.

    Create the directory if it isn't exist.

    Args:
        path (str): Directory's path
    """
    if not isdir(path):
        mkdir(path)


def sort(path_in: str, path_out: str):
    """Sort the content from a directory to another.

    The sort depend for each file on his date of creation/modification.
    Just like that:\n

    2020
     ↳ January
        ↳ 01
           ↳ ...

    Args:
        path_in (str): Source directory
        path_out (str): Destination directory
    """

    print("Checking source...")

    if not isdir(path_in):
        raise FileNotFoundError(f"""Directory "{path_in}" doesn't exist.""")

    print("Checking destination...")

    check_dir(path_out)

    print("Taking filepaths and pre-creating directories...")

    files: list = []
    files_len: int = 0

    for base, _, fps in walk(path_in):

        for fp in fps:

            fp_in: str = f"{base}/{fp}"
            date: datetime = datetime.fromtimestamp(getmtime(fp_in))

            fp_out = f"{path_out}/{date.year}"
            check_dir(fp_out)

            fp_out = f"{fp_out}/{date.strftime('%B')}"
            check_dir(fp_out)

            fp_out = f"{fp_out}/{date.strftime('%d')}"
            check_dir(fp_out)

            fp_out = f"{fp_out}/{fp}"
            if not fp_out in files and not isfile(fp_out):
                files.append([fp_in, fp_out])
                files_len += 1

    print(f"""Find {files_len} files in "{path_in}".""")
    print("Start copying files...")

    for fp_in, fp_out in files:

        print(f"""Copying "{fp_in}" to "{fp_out}"...""")
        Thread(target=copyfile, args=(fp_in, fp_out)).start()


if __name__ == "__main__":
    arg_len: int = len(argv)
    if arg_len == 2:
        sort(getcwd(), argv[1])
    elif arg_len == 3:
        sort(argv[1], argv[2])
    else:
        raise TypeError(
            f"Minimum 1 and maximum two arguments expected, but you give {arg_len - 1}")
