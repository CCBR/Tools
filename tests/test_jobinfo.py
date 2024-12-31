import argparse
import pytest

from ccbr_tools.jobinfo import get_jobinfo


def test_jobinfo():
    with pytest.raises(SystemExit) as exc_info:
        get_jobinfo(argparse.Namespace(joblist=["job1", "job2"]))
    assert str(exc_info.value) == "" and type(exc_info.value) is SystemExit
