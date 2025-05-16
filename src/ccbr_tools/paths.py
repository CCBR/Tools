import ast
import glob
import itertools
import json
import math
import pathlib
import tarfile
import warnings

from .shell import shell_run


def get_tree(pipeline_outdir, args="-aJ --du"):
    """
    Generate a directory tree structure using the `tree` command-line utility

    Note: when using -J with --du, the output is not valid JSON due to extra trailing commas.
    It can be parsed with `ast.literal_eval` rather than `json.loads`.

    Args:
        pipeline_outdir (str): The path to the directory for which the tree
            structure will be generated.
        args (str, optional): Additional arguments to pass to the `tree`
            command. Defaults to "-aJ" for including hidden files and formatting output as JSON

    Returns:
        str: The directory tree structure as a string, stripped of any
        leading or trailing whitespace.
    """
    return shell_run(f"tree {args} {pipeline_outdir}").strip()


def load_tree(tree_str):
    """
    Load a tree structure from a string, attempting to parse it as JSON or
    Python literal.

    Args:
        tree_str (str): The string representation of the tree structure.
    Returns:
        dict: The parsed tree structure as a dictionary.
    """
    try:
        # Attempt to parse the tree string as JSON
        tree_dict = json.loads(tree_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to parse it as Python literal
        # This is useful for tree output with trailing commas
        tree_dict = ast.literal_eval(tree_str)
        # warnings.warn(
        #     "Tree output has trailing commas, using ast.literal_eval instead of json.loads"
        # )
    return tree_dict


def get_disk_usage(tree_dict, pipeline_outdir):
    try:
        report = next(
            (
                item
                for item in tree_dict
                if isinstance(item, dict) and item.get("type") == "report"
            )
        )
        dir_size = report.get("size", math.nan)
    except StopIteration:  # occurs when there is no report in the tree dict
        dir_size = math.nan
    finally:
        if math.isnan(dir_size):
            # Fallback to using du command to determine disk usage
            warnings.warn(
                "Report or size not found in tree, using du to determine disk usage"
            )
            dir_size = run_du(pipeline_outdir)
    return dir_size


def run_du(dirpath):
    """
    Calculates the total size of a directory in bytes using the `du` shell command.

    Args:
        dirpath (str): Path to the directory whose size is to be calculated.
    Returns:
        int or float: The size of the directory in bytes. Returns NaN if the size cannot be determined.
    Raises:
        Issues a warning if the directory size cannot be parsed or if the `du` command fails.
    """
    try:
        dir_size = int(shell_run(f"du -bs {dirpath}").split("\t")[0])
    except Exception as e:
        warnings.warn(
            f"Error parsing directory size with du command for {dirpath}:\n{e}"
        )
        dir_size = math.nan
    return dir_size


def glob_files(
    pipeline_outdir,
    patterns=[
        "snakemake.log",
        ".nextflow.log",
        "*.jobby*",
        "master.log",
        "runtime_statics*",
    ],
):
    """
    Collects files from a specified directory and its subdirectories that match a list of patterns.

    Args:
        pipeline_outdir (str): The base directory to search for files.
        patterns (list of str, optional): A list of glob patterns to match files. Defaults to:
            [
                "snakemake.log",
                ".nextflow.log",
                "*.jobby*",
                "master.log",
                "runtime_statics*",
            ].

    Returns:
        set of pathlib.Path: A set of `pathlib.Path` objects representing the matched files.
    """
    return {
        pathlib.Path(f)
        for pattern in patterns
        for f in glob.glob(f"{pipeline_outdir}/**/{pattern}", recursive=True)
        if pathlib.Path(f).is_file()
    }


def create_tar_archive(files, tar_filename):
    """
    Creates a compressed tar archive (.tar.gz) containing the specified files.

    Args:
        files (list of pathlib.Path): A list of file paths to include in the archive.
        tar_filename (str): The name of the output tar.gz file.
    """
    with tarfile.open(tar_filename, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=file.name)
