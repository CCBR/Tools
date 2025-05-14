"""
SPOOKER 👻

This command is designed to be used as part of the OnComplete/OnSuccess/OnError handlers as part of Snakemake and Nextflow pipelines.
It collects metadata about the pipeline run, bundles it into a tarball, and saves it to a common location for later retrieval.

Run `spooker --help` for more information.
"""

import ast
import click
import datetime
import glob
import gzip
import itertools
import json
import os
import pathlib
import shutil
import tarfile
import warnings

from .shell import shell_run
from .pipeline import count_samples
from .pipeline.hpc import Cluster, list_modules, parse_modules
from .pkg_util import get_version, get_random_string, get_timestamp
from .jobby import jobby


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("outdir", type=click.Path(exists=True), default=pathlib.Path.cwd())
@click.argument("name", type=str, default="")
@click.argument("version", type=str, default="")
@click.argument("path", type=click.Path(), default="")
def cli(outdir, name, version, path):
    """
    spooker 👻

    This command is designed to be used as part of the OnComplete/OnSuccess/OnError handlers as part of Snakemake and Nextflow pipelines.
    It collects metadata about the pipeline run, bundles it into a tarball, and saves it to a common location for later retrieval.

    \b
    Args:
        outdir: Output directory for the pipeline run
        name: Name of the pipeline
        version: Version of the pipeline
        path: Path to the pipeline source
    """
    spooker(
        outdir,
        name,
        version,
        path,
    )


def spooker(
    pipeline_outdir: pathlib.Path,
    pipeline_version: str,
    pipeline_name: str,
    pipeline_path: str,
    clean=True,
    debug=False,
):
    """
    Processes a pipeline output directory to generate metadata, tree JSON, and SLURM job log JSON,
    then stages the file on an HPC cluster.

    Args:
        pipeline_outdir (pathlib.Path): Path to the pipeline output directory.
        pipeline_version (str): Version of the pipeline being processed.
        pipeline_name (str): Name of the pipeline being processed.
        pipeline_path (str): Path to the pipeline source code or configuration.
        clean (bool, optional): Whether to delete the generated metadata file after staging. Defaults to True.
        debug (bool, optional): Whether to enable debug mode for the HPC cluster. Defaults to False.

    Returns:
        pathlib.Path: Path to the staged metadata file on the HPC cluster.

    Raises:
        FileNotFoundError: If the pipeline output directory does not exist.

    Notes:
        - The function collects metadata, generates a tree JSON representation of the pipeline
          directory, and extracts job log information.
        - The metadata is written to a compressed JSON file and staged on an HPC cluster.
        - If `clean` is True, the local metadata file is deleted after staging.
    """
    pipeline_outdir = (
        pathlib.Path(pipeline_outdir)
        if not isinstance(pipeline_outdir, pathlib.Path)
        else pipeline_outdir
    )
    if not pipeline_outdir.exists():
        raise FileNotFoundError(
            f"Pipeline output directory does not exist: {pipeline_outdir}"
        )

    metadata = {}
    # tree json
    tree_str = get_tree(pipeline_outdir)
    metadata["outdir_tree"] = tree_str

    # pipeline metadata
    metadata["pipeline_metadata"] = collect_metadata(
        pipeline_outdir, pipeline_version, pipeline_name, pipeline_path, tree_str
    )
    timestamp = metadata["pipeline_metadata"]["date"]

    # jobby json
    log_file = glob_files(
        pipeline_outdir, patterns=["snakemake.log", ".nextflow.log"]
    ).pop()
    metadata["jobby"] = json.dumps(jobby([log_file, "--json"]))

    # TODO master job log
    metadata["master_job_log"] = {"txt": None}
    # TODO failed jobs logfiles
    metadata["failed_jobs"] = {}

    # write metadata to json
    meta_outfilename = pipeline_outdir / f"{timestamp}.json.gz"
    with gzip.open(meta_outfilename, "wt") as outfile:
        json.dump(metadata, outfile, indent=4)

    # copy to staging directory
    hpc = Cluster.create_hpc(debug=debug)
    spook_outfilename = hpc.spook(
        file=meta_outfilename,
        subdir=f"{get_random_string()}_{metadata['pipeline_metadata']['user']}_{timestamp}",
    )

    # optional cleanup
    if clean:
        meta_outfilename.unlink()
    return spook_outfilename


def collect_metadata(
    pipeline_outdir: pathlib.Path,
    pipeline_version: str,
    pipeline_name: str,
    pipeline_path: str,
    timestamp=get_timestamp(),
    tree_str="{}",
):
    """
    Collect metadata for the pipeline run and save it to a file.

    Args:
        pipeline_outdir (pathlib.Path): The output directory for the pipeline run.
        pipeline_version (str): The version of the pipeline.
        pipeline_name (str): The name of the pipeline.
        pipeline_path (str): The path to the pipeline source.
        timestamp (str, optional): The timestamp of the pipeline run. Defaults to using `~ccbr_tools.pkg_util.get_timestamp()`.
    """
    tree_dict = load_tree(tree_str)
    outdir_size = get_disk_usage(tree_dict, pipeline_outdir)
    ccbrpipeliner_version = parse_modules(list_modules()).get(
        "ccbrpipeliner", "unknown"
    )
    groups = shell_run("groups").strip()

    # TODO: determine nsamples, different logic for each pipeline
    nsamples = count_samples(tree_str, pipeline_name)

    metadata = {
        "pipeline_name": pipeline_name,
        "pipeline_path": str(pipeline_path),
        "pipeline_outdir": str(pipeline_outdir),
        "pipeline_outdir_size": outdir_size,
        "pipeline_version": pipeline_version,
        "ccbrpipeliner_module": ccbrpipeliner_version,
        "user": os.environ.get("USER"),
        "uid": os.environ.get("UID"),
        "groups": groups,
        "date": timestamp,
        "nsamples": nsamples,
    }
    return metadata


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
        warnings.warn(
            "Tree output has trailing commas, using ast.literal_eval instead of json.loads"
        )
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
        for f in itertools.chain(
            glob.glob(
                f"{pipeline_outdir}/{pattern}",
            ),
            glob.glob(f"{pipeline_outdir}/**/{pattern}"),
        )
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


def main():
    cli()


if __name__ == "__main__":
    cli()
