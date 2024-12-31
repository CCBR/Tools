import argparse
import pytest

import ccbr_tools.homologfinder.hf as hf
from ccbr_tools.shell import shell_run


def test_hf_gene():
    assert hf.hf(argparse.Namespace(gene="ZNF365", genelist="", genelistfile="")) == [
        "Zfp365"
    ]


def test_hf_list():
    assert hf.hf(
        argparse.Namespace(gene="", genelist="Wdr53,Zfp365", genelistfile="")
    ) == ["WDR53", "ZNF365"]


def test_hf_file():
    assert hf.hf(
        argparse.Namespace(gene="", genelist="", genelistfile="tests/data/genelist.txt")
    ) == ["WDR53", "ZNF365"]


def test_hf_cli_err():
    out = shell_run("hf -g a -l b -f c")
    assert "Only one can be provided -g or -l or -f" in out
