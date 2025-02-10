import argparse
import pytest

from ccbr_tools.shell import shell_run
from ccbr_tools.jobinfo import get_jobinfo, check_host, mem2gb, time2sec


def test_jobinfo_cli():
    out = shell_run("python -m ccbr_tools.jobinfo -j 123456")
    assert "This script only works on BIOWULF!" in out


def test_jobinfo():
    with pytest.raises(SystemExit) as exc_info:
        get_jobinfo(argparse.Namespace(joblist=["job1", "job2"]))
    assert str(exc_info.value) == "" and type(exc_info.value) is SystemExit


def test_check_host():
    with pytest.raises(SystemExit) as exc_info:
        check_host()
    assert str(exc_info.value) == "" and type(exc_info.value) is SystemExit


def test_mem2gb():
    assert all(
        [
            mem2gb("0") == 0.0,
            mem2gb("3.5 GB") == 3.5,
            mem2gb("1024 MB") == 1.0,
            mem2gb("1048576 KB") == 1.0,
        ]
    )


def test_time2sec():
    assert time2sec("0-00:01:00") == 60.0
