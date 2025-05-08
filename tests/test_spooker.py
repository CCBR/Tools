import pathlib
import pytest
from pprint import pprint
import gzip
import json


from ccbr_tools.spooker import spooker
from ccbr_tools.shell import shell_run


@pytest.mark.filterwarnings("ignore:UserWarning")
def test_spooker():
    out_filename = spooker(
        pipeline_outdir=pathlib.Path("tests/data/pipeline_run"),
        pipeline_version="0.1.0",
        pipeline_name="test_pipeline",
        pipeline_path="unknown",
        clean=True,
        debug="gha",
    )
    with gzip.open(out_filename, "rt") as file:
        spook_dat = json.load(file)
    pprint(spook_dat)
    assert set(
        {
            "ccbrpipeliner_module": "unknown",
            "jobby_json": '""',
            "pipeline_name": "test_pipeline",
            "pipeline_outdir": "tests/data/pipeline_run",
            "pipeline_outdir_size": "3005",
            "pipeline_path": "unknown",
            "pipeline_version": "0.1.0",
        }.items()
    ).issubset(set(spook_dat.items()))


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
    assert "Usage: spooker " in shell_run("spooker --help")
