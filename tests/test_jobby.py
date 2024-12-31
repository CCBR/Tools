import argparse
import pytest

from ccbr_tools.shell import exec_in_context
from ccbr_tools.jobby import (
    jobby,
    which,
    get_toolkit,
    add_missing,
    convert_size,
    to_bytes,
    sge,
    uge,
)


def test_jobby_scheduler():
    args = argparse.Namespace(
        JOB_ID="abc", scheduler="unknown", threads=1, tmp_dir="/tmp"
    )
    with pytest.raises(SystemExit) as exc_info:
        exec_in_context(jobby, args)
    assert str(exc_info.value) == "1"


def test_jobby_slurm():
    args = argparse.Namespace(
        JOB_ID="abc", scheduler="slurm", threads=1, tmp_dir="/tmp"
    )
    with pytest.raises(SystemExit) as exc_info:
        exec_in_context(jobby, args)
    assert str(exc_info.value) == "1"


def test_which():
    assert all([which("ls"), not which("unknown")])


def test_get_toolkit():
    assert get_toolkit(["ls", "notATool"]) == "ls"


def test_add_missing():
    outlist = add_missing([0, 1, 2, 3, 4], {3: ["+", "++"], 1: "-", 4: "@"})
    assert outlist == [0, "-", 1, 2, "+", "++", 3, "@", 4]


def test_convert_size():
    assert all(
        [
            convert_size(1024) == "1.0KiB",
            convert_size(0) == "0B",
            convert_size(1024 * 1024) == "1.0MiB",
        ]
    )


def test_to_bytes():
    assert all(
        [
            to_bytes("1.0KiB") == 1024,
            to_bytes("0B") == 0,
            to_bytes("1.0MiB") == 1024 * 1024,
        ]
    )


def test_sge():
    with pytest.raises(NotImplementedError) as exc_info:
        sge("", "", "")
    assert str(exc_info.value) == "SGE cluster support is not yet implemented!"


def test_uge():
    with pytest.raises(NotImplementedError) as exc_info:
        uge("", "", "")
    assert str(exc_info.value) == "UGE cluster support is not yet implemented!"
