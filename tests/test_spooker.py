import math
import pathlib
import pytest
from pprint import pprint
import gzip
import json
import subprocess
import tempfile


from ccbr_tools.spooker import spooker


@pytest.mark.filterwarnings("ignore:UserWarning")
def test_spooker():
    out_filename = spooker(
        pipeline_outdir=pathlib.Path("tests/data/pipeline_run"),
        pipeline_name="test_pipeline",
        pipeline_version="0.1.0",
        pipeline_path="unknown",
        clean=True,
        debug="gha",
    )
    with gzip.open(out_filename, "rt") as file:
        spook_dat = json.load(file)
    # pprint(spook_dat)
    expected = {
        "ccbrpipeliner_module": None,
        "pipeline_name": "test_pipeline",
        "pipeline_outdir": "tests/data/pipeline_run",
        "pipeline_path": "unknown",
        "pipeline_version": "0.1.0",
        "sample_names": [],
    }
    actual = {
        k: v for k, v in spook_dat["pipeline_metadata"].items() if k in expected.keys()
    }
    assert actual == expected


def test_spooker_no_outdir():
    with pytest.raises(FileNotFoundError) as exc_info:
        spooker(
            pipeline_outdir=pathlib.Path("tests/data/pipeline_run/does_not_exist"),
            pipeline_version="0.1.0",
            pipeline_name="test_pipeline",
            pipeline_path="unknown",
            clean=True,
            debug="gha",
        )
    assert str(exc_info.value).startswith("Pipeline output directory does not exist")


def test_spooker_cli():
    out = subprocess.run(
        "spooker --outdir tests/data/pipeline_run --name test_pipeline --version 0.1.2-dev --path unknown --debug gha",
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    print("OUT", out)
    out_filename = out.split()[-1]
    with gzip.open(out_filename, "rt") as file:
        spook_dat = json.load(file)

    expected_meta = {
        "ccbrpipeliner_module": None,
        "pipeline_name": "test_pipeline",
        "pipeline_outdir": "tests/data/pipeline_run",
        "pipeline_path": "unknown",
        "pipeline_version": "0.1.2-dev",
        "sample_names": [],
    }
    actual_meta = {
        k: v
        for k, v in spook_dat["pipeline_metadata"].items()
        if k in expected_meta.keys()
    }
    assert all(
        [
            expected_meta == actual_meta,
            spook_dat.keys()
            == {"outdir_tree", "pipeline_metadata", "jobby", "master_job_log"},
        ]
    )


def test_spooker_help():
    assert (
        "Usage: spooker "
        in subprocess.run(
            "spooker --help", shell=True, capture_output=True, text=True
        ).stdout
    )
