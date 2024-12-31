import pytest

import ccbr_tools.gb2gtf as gb2gtf


def test_check_args():
    test_cases = [
        (["", "test"], True),
        (["test"], False),
        (["test", "-h"], False),
        (["test", "--help"], False),
    ]
    assert all([gb2gtf.check_args(args) == expected for args, expected in test_cases])


def test_gb2gtf_err():
    with pytest.raises(SystemExit) as exc_info:
        gb2gtf.gb2gtf(["", "tests/data/sequence_U49845.gb"])
    assert str(exc_info.value) == "Something fishy!"
