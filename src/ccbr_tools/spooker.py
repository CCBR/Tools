import datetime
import glob
import itertools
import os
import pathlib
import ruamel.yaml
import shutil
import tarfile

from .shell import shell_run
from .pipeline.hpc import Cluster, list_modules, parse_modules


def spooker(
    pipeline_outdir: pathlib.Path,
    pipeline_version: str,
    pipeline_name: str,
    pipeline_path: str,
    clean=True,
):
    if not pipeline_outdir.exists():
        raise FileNotFoundError(
            f"Pipeline output directory does not exist: {pipeline_outdir}"
        )

    # metadata
    metadata = collect_metadata(
        pipeline_outdir,
        pipeline_version,
        pipeline_name,
        pipeline_path,
    )
    date = metadata["DATE"]
    meta_outfilename = pipeline_outdir / f"{date}.yml"
    write_metadata(
        metadat,
        meta_outfilename,
    )

    # tree json
    tree_outfilename = pipeline_outdir / f"{date}.tree.json"
    write_tree(get_tree(pipeline_outdir, args="-J"), tree_outfilename)

    # create tar archive, include log files
    tar_filename = pipeline_outdir / f"{date}.tar.gz"
    files = glob_files(pipeline_outdir)
    files.update(meta_outfilename, tree_outfilename)
    create_tar_archive(files, tar_filename)

    # copy to staging directory
    spook_dir = Cluster.create_hpc().SPOOK_DIR
    if spook_dir.is_dir() and spook_dir.is_writable():
        shutil.copy(tar_filename, spook_dir)

    # optional cleanup
    if clean:
        for file in (
            meta_outfilename,
            tree_outfilename,
            tar_filename,
        ):
            file.unlink()


def collect_metadata(
    pipeline_outdir: pathlib.Path,
    pipeline_version: str,
    pipeline_name: str,
    pipeline_path: str,
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
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    metadata_caps = {key.upper(): val for key, val in metadata.items()}
    return metadata_caps


def write_metadata(metadata, outfilename):
    with open(outfilename, "w") as outfile:
        yaml.dump(metadata, outfile)


def get_tree(pipeline_outdir, args="-J"):
    return shell_run(f"tree {pipeline_outdir} {args}").strip()


def write_tree(tree: str, outfilename):
    yaml = ruamel.yaml.YAML(typ="rt")
    with open(outfilename, "w") as outfile:
        yaml.dump(tree, outfile)


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
        pathlib.path(f)
        for f in itertools.chain(
            glob.glob(
                f"{pipeline_outdir}/{pattern}",
            ),
            glob.glob(f"{pipeline_outdir}/**/{pattern}"),
        )
        for pattern in patterns
        if pathlib.path(f).is_file()
    }


def create_tar_archive(files, tar_filename):
    with tarfile.open(tar_filename, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=file.basename())
