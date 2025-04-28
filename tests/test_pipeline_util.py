import argparse
import os
import pathlib
import tempfile

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


def test_copy_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        copy_config(
            ("file.txt", "file2.txt"),
            repo_base=lambda f: pathlib.Path(__file__).absolute().parent / "data" / f,
            outdir=tmp_dir,
        )
        assert all(
            [
                (tmp_dir / "file.txt").exists(),
                (tmp_dir / "file2.txt").exists(),
                not (tmp_dir / "file.fa").exists(),
            ]
        )


def test_tmp_dir():
    assert all(
        [
            get_tmp_dir("", "./out", hpc="biowulf").startswith("/lscratch"),
            get_tmp_dir("", "./out", hpc="frce").startswith("./out"),
            get_tmp_dir("", "./out", hpc="none") == None,
        ]
    )


def test_get_mtime():
    mtime = _get_file_mtime("tests/data/file.txt")
    assert all([len(mtime) == 12, mtime.isdigit()])


def test_get_genomes_dict():
    d = get_genomes_dict(repo_base)
    assert d == {}


def test_md5sum():
    assert all(
        [
            md5sum("tests/data/file.txt") == "47ece2e49e5c0333677fc34e044d8257",
            md5sum("tests/data/file2.txt") == "04ab3457e5e52c208c1af0139ad47d25",
        ]
    )


def test_permissions():
    abspath = permissions(argparse.ArgumentParser(), "tests/data/file.txt", os.R_OK)
    assert abspath.endswith("tests/data/file.txt")


def test_exists():
    assertions = [
        pathlib.Path(p).exists() == exists(p)
        for p in ["tests/data/file.txt", "tests/data/file2.txt", "not/a/path"]
    ]
    assert all(assertions)


def test_which():
    assert all([which("ls"), not which("unknown")])
