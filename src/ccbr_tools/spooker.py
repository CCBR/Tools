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
    SPOOKER 👻

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
    tree_str = get_tree(pipeline_outdir, args="-J")
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


def get_tree(pipeline_outdir, args="-J"):
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
    with tarfile.open(tar_filename, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=file.name)


def main():
    cli()


if __name__ == "__main__":
    cli()
