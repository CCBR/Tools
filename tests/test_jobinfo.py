import argparse
import json
import sys
import pytest

from ccbr_tools.shell import shell_run
from ccbr_tools.jobinfo import get_jobinfo, check_host, mem2gb, time2sec


def test_jobinfo_cli():
    out = shell_run(f"{sys.executable} -m ccbr_tools.jobinfo -j 123456")
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


def test_get_jobinfo_parses_output(monkeypatch, tmp_path):
    sample = [
        {
            "jobid": "123",
            "jobname": "test",
            "state": "COMPLETED",
            "state_reason": "None",
            "eval": "0",
            "exit_code": "0:0",
            "nodelist": "node1",
            "partition": "test",
            "qos": "normal",
            "submit_time": "2024-01-01T00:00:00",
            "queued_time": "0-00:01:00",
            "queued_time_seconds": "60",
            "elapsed_time": "0-00:02:00",
            "elapsed_time_seconds": "120",
            "timelimit": "0-00:10:00",
            "timelimit_seconds": "600",
            "user": "user",
            "cpus": "2",
            "cpu_min": "-",
            "cpu_avg": "-",
            "cpu_max": "1.0",
            "mem": "1 GB",
            "mem_min": "-",
            "mem_avg": "-",
            "mem_max": "0.5 GB",
            "gres": "-",
            "work_dir": "/tmp",
            "std_out": "/tmp/out",
            "std_err": "/tmp/err",
        }
    ]

    class DummyProc:
        def __init__(self, stdout):
            self.returncode = 0
            self.stdout = stdout

    def fake_run(*_args, **_kwargs):
        return DummyProc(json.dumps(sample))

    monkeypatch.setattr("ccbr_tools.jobinfo.subprocess.run", fake_run)
    output_path = tmp_path / "jobinfo.tsv"
    args = argparse.Namespace(joblist=["123"], output=str(output_path), failonly=False)
    table = get_jobinfo(args)

    assert output_path.exists()
    assert "max_cpu_util" in table.columns
    assert "max_mem_util" in table.columns
    assert "time_util" in table.columns
    assert table.iloc[0]["time_util"] == "20.00 %"
