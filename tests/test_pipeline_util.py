import argparse
import os
import pathlib

from ccbr_tools.pipeline.util import (
    copy_config,
    get_tmp_dir,
    _get_file_mtime,
    get_genomes_dict,
    md5sum,
    permissions,
    exists,
    which,
)
from ccbr_tools.pkg_util import repo_base


def test_copy_config(tmp_path, data_dir):
    copy_config(
        ("file.txt", "file2.txt"),
        repo_base=lambda f: data_dir / f,
        outdir=tmp_path,
    )
    assert (tmp_path / "file.txt").exists()
    assert (tmp_path / "file2.txt").exists()
    assert not (tmp_path / "file.fa").exists()


def test_tmp_dir():
    assert get_tmp_dir("", "./out", hpc="biowulf").startswith("/lscratch")
    assert get_tmp_dir("", "./out", hpc="frce").startswith("./out")
    assert get_tmp_dir("", "./out", hpc="none") is None


def test_get_mtime(data_dir):
    mtime = _get_file_mtime(data_dir / "file.txt")
    assert len(mtime) == 12
    assert mtime.isdigit()


def test_get_genomes_dict():
    d = get_genomes_dict(repo_base)
    assert d == {}


def test_md5sum(data_dir):
    assert md5sum(data_dir / "file.txt") == "47ece2e49e5c0333677fc34e044d8257"
    assert md5sum(data_dir / "file2.txt") == "04ab3457e5e52c208c1af0139ad47d25"


def test_permissions(data_dir):
    abspath = permissions(argparse.ArgumentParser(), data_dir / "file.txt", os.R_OK)
    assert abspath.endswith("tests/data/file.txt")


def test_exists(data_dir):
    assertions = [
        pathlib.Path(p).exists() == exists(p)
        for p in [data_dir / "file.txt", data_dir / "file2.txt", "not/a/path"]
    ]
    assert assertions[0]
    assert assertions[1]
    assert assertions[2]


def test_which():
    assert which("ls")
    assert not which("unknown")
