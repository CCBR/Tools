"""
SPOOKER 👻

This command is designed to be used as part of the OnComplete/OnSuccess/OnError handlers as part of Snakemake and Nextflow pipelines.
It collects metadata about the pipeline run, bundles it into a tarball, and saves it to a common location for later retrieval.

Run `spooker --help` for more information.

See [](`~ccbr_tools.spooker.spooker`) for the main function
"""

import click
import gzip
import json
import os
import pathlib

from .paths import get_tree, load_tree, get_disk_usage, glob_files
from .pipeline import count_pipeline_samples
from .pipeline.hpc import Cluster, list_modules, parse_modules
from .pkg_util import get_version, get_random_string, get_timestamp
from .jobby import jobby, get_failed_job_logs
from .shell import get_groups, shell_run


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
    pipeline_name: str,
    pipeline_version: str,
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
    metadata = get_spooker_dict(
        pipeline_outdir, pipeline_name, pipeline_version, pipeline_path
    )
    timestamp = metadata["pipeline_metadata"]["date"]

    # write metadata to json
    meta_outfilename = pipeline_outdir / f"{timestamp}.json.gz"
    with gzip.open(meta_outfilename, "wt") as outfile:
        json.dump(metadata, outfile, indent=4)
    assert meta_outfilename.exists()

    # copy to staging directory
    hpc = Cluster.create_hpc(debug=debug)
    spook_outfilename = hpc.spook(
        file=meta_outfilename,
        subdir=f"{get_random_string()}_{metadata['pipeline_metadata']['user']}_{timestamp}",
    )
    assert spook_outfilename.exists()

    # optional cleanup
    if clean:
        meta_outfilename.unlink()
    print(f"Metadata staged to {spook_outfilename}")
    return spook_outfilename


def get_spooker_dict(
    pipeline_outdir: pathlib.Path,
    pipeline_name: str,
    pipeline_version: str,
    pipeline_path: str,
):
    """
    Generates a metadata dictionary summarizing the state and logs of a pipeline run.

    Args:
        pipeline_outdir (pathlib.Path): Path to the pipeline output directory.
        pipeline_name (str): Name of the pipeline.
        pipeline_version (str): Version of the pipeline.
        pipeline_path (str): Path to the pipeline definition or script.

    Returns:
        dict: A dictionary containing:
            - "outdir_tree": String representation of the output directory tree.
            - "pipeline_metadata": Metadata about the pipeline run.
            - "jobby": JSON-formatted job log records.
            - "master_job_log": Contents of the main job log file.
            - "failed_jobs": Logs of failed jobs.
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
    metadata["pipeline_metadata"] = collect_pipeline_metadata(
        pipeline_outdir, pipeline_version, pipeline_name, pipeline_path, tree_str
    )
    timestamp = metadata["pipeline_metadata"]["date"]

    # jobby & logs
    log_file = glob_files(
        pipeline_outdir, patterns=["snakemake.log", ".nextflow.log"]
    ).pop()
    jobby_df = jobby([log_file])
    metadata["jobby"] = jobby_df.to_json(orient="records", indent=2)
    with open(log_file, "r") as infile:
        metadata["master_job_log"] = {"txt": infile.read()}
    metadata["failed_jobs"] = get_failed_job_logs(jobby_df.to_dict(orient="records"))
    return metadata


def collect_pipeline_metadata(
    pipeline_outdir: pathlib.Path,
    pipeline_version: str,
    pipeline_name: str,
    pipeline_path: str,
    tree_str="{}",
    timestamp=get_timestamp(),
):
    """
    Collect metadata for the pipeline run

    Args:
        pipeline_outdir (pathlib.Path): The output directory for the pipeline run.
        pipeline_version (str): The version of the pipeline.
        pipeline_name (str): The name of the pipeline.
        pipeline_path (str): The path to the pipeline source.
        tree_str (str, optional): The JSON string representation of the pipeline output directory tree. Defaults to "{}".
        timestamp (str, optional): The timestamp of the pipeline run. Defaults to using `~ccbr_tools.pkg_util.get_timestamp()`.
    """
    tree_dict = load_tree(tree_str)
    outdir_size = get_disk_usage(tree_dict, pipeline_outdir)
    ccbrpipeliner_version = parse_modules(list_modules()).get(
        "ccbrpipeliner", "unknown"
    )
    groups = get_groups()
    nsamples = count_pipeline_samples(tree_str, pipeline_name)

    metadata = {
        "pipeline_name": pipeline_name,
        "pipeline_path": str(pipeline_path),
        "pipeline_outdir": str(pipeline_outdir),
        "pipeline_outdir_size": outdir_size,
        "pipeline_version": pipeline_version,
        "ccbrpipeliner_module": ccbrpipeliner_version,
        "user": os.environ.get("USER"),
        "uid": shell_run("echo $UID").strip(),
        "groups": groups,
        "date": timestamp,
        "nsamples": nsamples,
    }
    return metadata


def main():
    cli()


if __name__ == "__main__":
    cli()
