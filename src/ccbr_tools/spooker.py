"""
SPOOKER 👻

This command is designed to be used as part of the OnComplete/OnSuccess/OnError handlers as part of Snakemake and Nextflow pipelines.
It collects metadata about the pipeline run, bundles it into a tarball, and saves it to a common location for later retrieval.

Run `spooker --help` for more information.
"""

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

from .shell import shell_run
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

    # metadata
    metadata = collect_metadata(
        pipeline_outdir, pipeline_version, pipeline_name, pipeline_path
    )
    timestamp = metadata["date"]

    # tree json
    tree_str = get_tree(pipeline_outdir)
    metadata["tree_json"] = tree_str

    # TODO: determine nsamples, different logic for each pipeline
    tree_json = json.loads(tree_str)

    # jobby json
    log_file = glob_files(
        pipeline_outdir, patterns=["snakemake.log", ".nextflow.log"]
    ).pop()
    metadata["jobby_json"] = json.dumps(jobby([log_file, "--json"]))

    # write metadata to json
    meta_outfilename = pipeline_outdir / f"{timestamp}.json.gz"
    with gzip.open(meta_outfilename, "wt") as outfile:
        json.dump(metadata, outfile, indent=4)

    # copy to staging directory
    hpc = Cluster.create_hpc(debug=debug)
    spook_outfilename = hpc.spook(
        file=meta_outfilename,
        subdir=f"{get_random_string()}_{metadata['user']}_{timestamp}",
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
):
    """
    Collect metadata for the pipeline run and save it to a file.

    Args:
        pipeline_outdir (pathlib.Path): The output directory for the pipeline run.
        pipeline_version (str): The version of the pipeline.
        pipeline_name (str): The name of the pipeline.
        pipeline_path (str): The path to the pipeline source.
    """
    outdir_size = shell_run(f"du -bs {pipeline_outdir}").split("\t")[0]
    ccbrpipeliner_version = parse_modules(list_modules()).get(
        "ccbrpipeliner", "unknown"
    )
    groups = shell_run("groups").strip()
    metadata = {
        "pipeline_outdir": str(pipeline_outdir),
        "pipeline_outdir_size": outdir_size,
        "pipeline_name": pipeline_name,
        "pipeline_path": str(pipeline_path),
        "pipeline_version": pipeline_version,
        "ccbrpipeliner_module": ccbrpipeliner_version,
        "user": os.environ.get("USER"),
        "date": timestamp,
    }
    return metadata


def get_tree(pipeline_outdir, args="-aJ"):
    """
    Generate a directory tree structure using the `tree` command-line utility

    Args:
        pipeline_outdir (str): The path to the directory for which the tree
            structure will be generated.
        args (str, optional): Additional arguments to pass to the `tree`
            command. Defaults to "-aJ" for including hidden files and formatting output as JSON

    Returns:
        str: The directory tree structure as a string, stripped of any
        leading or trailing whitespace.
    """
    return shell_run(f"tree {pipeline_outdir} {args}").strip()


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
