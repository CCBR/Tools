import pytest
import ccbr_tools.intersect
from ccbr_tools.shell import exec_in_context


def test_intersect():
    out = exec_in_context(
        ccbr_tools.intersect.main,
        ["intersect", "tests/data/file.txt", "tests/data/file2.txt", 0, 0],
    )
    assert out == "d\td\nb\tb\n"


def test_intersect_err():
    with pytest.raises(IndexError) as exc_info:
        exec_in_context(
            ccbr_tools.intersect.main,
            ["intersect", "tests/data/file.txt", "tests/data/file2.txt", 0, 1],
        )
    assert str(exc_info.value) == "list index out of range"


def test_intersect_help():
    out = exec_in_context(
        ccbr_tools.intersect.main,
        ["intersect", "--help", "tests/data/file.txt", "tests/data/file2.txt", 0, 0],
    )
    assert out.startswith("USAGE:\nintersect")


def test_intersect_usage():
    with pytest.raises(SystemExit):
        out = exec_in_context(ccbr_tools.intersect.main, [])
        assert out.startswith("INCORRECT USAGE:")
