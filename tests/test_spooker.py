import pathlib
import pytest
import tarfile
import ruamel.yaml

from ccbr_tools.spooker import (
    spooker,
    collect_metadata,
    write_metadata,
    get_tree,
    write_tree,
    glob_files,
    create_tar_archive,
    spook,
)
from ccbr_tools.shell import shell_run

yaml = ruamel.yaml.YAML(typ="rt")


@pytest.mark.filterwarnings("ignore:UserWarning")
def test_spooker():
    out_tarpath = spooker(
        pipeline_outdir=pathlib.Path("tests/data/pipeline_run"),
        pipeline_version="0.1.0",
        pipeline_name="test_pipeline",
        pipeline_path="unknown",
        clean=True,
        debug="gha",
    )
    with tarfile.open(out_tarpath, "r:gz") as tar:
        files = sorted(tar.getnames())
        timestamp = files[0].split(".")[0]
        members = {f.name: f for f in tar.getmembers()}
        metadata = yaml.load(tar.extractfile(members[f"{timestamp}.yml"]).read())
    assert all(
        [
            sorted([".".join(f.split(".")[1:]) for f in files])
            == ["jobby.json", "log", "tree.json", "yml"],
            metadata["PIPELINE_NAME"] == "test_pipeline",
            metadata["PIPELINE_VERSION"] == "0.1.0",
            metadata["PIPELINE_PATH"] == "unknown",
            metadata["CCBRPIPELINER_MODULE"] == "unknown",
            len(metadata["USER"]) > 0,
            len(metadata["DATE"]) == len("2025-05-06T12-47-12"),
        ]
    )


def test_spooker_cli():
    assert "Usage: spooker " in shell_run("spooker --help")
