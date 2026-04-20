import pytest
import ccbr_tools.intersect
from ccbr_tools.shell import exec_in_context


def test_intersect(data_dir_rel):
    out = exec_in_context(
        ccbr_tools.intersect.run_intersect,
        [
            "intersect",
            str(data_dir_rel / "file.txt"),
            str(data_dir_rel / "file2.txt"),
            0,
            0,
        ],
    )
    assert out == "d\td\nb\tb\n"


def test_intersect_err(data_dir_rel):
    with pytest.raises(IndexError) as exc_info:
        exec_in_context(
            ccbr_tools.intersect.run_intersect,
            [
                "intersect",
                str(data_dir_rel / "file.txt"),
                str(data_dir_rel / "file2.txt"),
                0,
                1,
            ],
        )
    assert str(exc_info.value) == "list index out of range"


def test_intersect_help(data_dir_rel):
    out = exec_in_context(
        ccbr_tools.intersect.run_intersect,
        [
            "intersect",
            "--help",
            str(data_dir_rel / "file.txt"),
            str(data_dir_rel / "file2.txt"),
            0,
            0,
        ],
    )
    assert out.startswith("USAGE:\nintersect")


def test_intersect_usage():
    with pytest.raises(SystemExit):
        out = exec_in_context(ccbr_tools.intersect.run_intersect, [])
        assert out.startswith("INCORRECT USAGE:")
