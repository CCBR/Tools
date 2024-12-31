from ccbr_tools.shell import shell_run

import pytest
import sys

import ccbr_tools.GSEA.deg2gs as deg2gs
import ccbr_tools.GSEA.ncbr_huse as ncbr_huse
import ccbr_tools.GSEA.multitext2excel as mt2excel


def test_help_deg():
    assert shell_run("python -m ccbr_tools.GSEA.deg2gs -h").startswith(
        "usage: deg2gs.py"
    )


def test_help_mt2excel():
    assert shell_run("python -m ccbr_tools.GSEA.multitext2excel -h").startswith(
        "usage: multitext2excel.py"
    )


def test_run_cmd():
    assert not ncbr_huse.run_cmd(["echo", "hello"], sys.stdout, True)


def test_run_os_cmd():
    assert not ncbr_huse.run_os_cmd(["echo", "hello"], sys.stdout, True)


def test_un_gzip():
    assert not ncbr_huse.un_gzip("tests/data/file.txt", sys.stdout)


def test_send_update():
    assert ncbr_huse.send_update("hello world", log=sys.stderr, quiet=False) == 0


def test_err_out():
    with pytest.raises(SystemExit) as exc_info:
        ncbr_huse.err_out("custom error", log=sys.stderr)
    assert str(exc_info.value) == "custom error"


def test_fasta_count():
    assert all(
        [
            ncbr_huse.fasta_count("tests/data/file.fa") == 2,
            ncbr_huse.fasta_count("tests/data/file.txt") == 0,
        ]
    )


def test_fasta_list():
    assert all(
        [
            ncbr_huse.fasta_list("tests/data/file.fa") == ["a", "b"],
            ncbr_huse.fasta_list("tests/data/file.txt") == [],
        ]
    )
