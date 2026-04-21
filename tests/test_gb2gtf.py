import pytest

import ccbr_tools.gb2gtf as gb2gtf
from ccbr_tools.shell import exec_in_context


def test_check_args():
    test_cases = [
        (["", "test"], True),
        (["test"], False),
        (["test", "-h"], False),
        (["test", "--help"], False),
    ]
    assert [gb2gtf.check_args(args) for args, _ in test_cases] == [
        expected for _, expected in test_cases
    ]


def test_gb2gtf_err(data_dir_rel):
    with pytest.raises(SystemExit) as exc_info:
        gb2gtf.gb2gtf(["", str(data_dir_rel / "sequence_U49845.gb")])
    assert str(exc_info.value) == "Something fishy!"


def test_gb2gtf(data_dir_rel):
    out = exec_in_context(
        gb2gtf.gb2gtf, ["", str(data_dir_rel / "sequence_AF165912.gb")]
    )
    gtf = (data_dir_rel / "snapshots" / "sequence_AF165912.gtf").read_text()
    assert out == gtf


if __name__ == "__main__":
    out = exec_in_context(gb2gtf.gb2gtf, ["", "tests/data/sequence_AF165912.gb"])
    with open("tests/data/snapshots/sequence_AF165912.gtf", "w") as f:
        f.write(out)
