""" Miscellaneous utility functions """

import contextlib
import io
import os
import subprocess


def repo_base(*paths):
    """Get the absolute path to a file in the repository
    @return abs_path <str>
    """
    basedir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    return os.path.join(basedir, *paths)


def get_version():
    """Get the current version
    @return version <str>
    """
    with open(repo_base("VERSION"), "r") as vfile:
        version = f"v{vfile.read().strip()}"
    return version
