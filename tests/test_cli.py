from ccbr_tools.shell import shell_run

import os
import pathlib
import pytest

is_ci = (
    os.environ.get("CI", "false") == "true"
)  # Set CI to false if not in a CI environment


def test_version_flag():
    """Test version flag."""
    version = shell_run("ccbr_tools --version")
    assert version.startswith("ccbr_tools, version ")


@pytest.mark.skipif(is_ci, reason="Skip on CI")
def test_version_cmd():
    """Test version cmd."""
    version = shell_run("ccbr_tools version --debug")
    assert version.startswith("VERSION file path")


def test_help():
    """Test help."""
    assert "Utilities for CCBR Bioinformatics Software" in shell_run("ccbr_tools -h")


def test_help_cite():
    """Test help cite."""
    assert "Print the citation in the desired format" in shell_run("ccbr_tools cite -h")


def test_help_gb2gtf():
    """Test help gb2gtf."""
    assert "Usage: gb2gtf sequence.gb > sequence.gtf" in shell_run("gb2gtf -h")


def test_help_hf():
    """Test help hf."""
    assert "Get Human2Mouse (or Mouse2Human) homolog gene or genelist" in shell_run(
        "hf -h"
    )


def test_help_jobby():
    """Test help jobby."""
    assert "jobby <jobid1> [jobid2 ...] " in shell_run("jobby -h")


def test_help_jobinfo():
    """Test help jobinfo."""
    jobinfo_help = shell_run("jobinfo -h")
    assert (
        "Get HPC usage metadata for a list of slurm jobids on biowulf" in jobinfo_help
    )


def test_help_intersect():
    """Test help intersect."""
    assert "intersect filename1 filename2 f1ColumnIndex F2ColumnIndex" in shell_run(
        "intersect -h"
    )


def test_help_peek():
    """Test help peek."""
    assert "USAGE: peek <file.tsv> [buffer]" in shell_run("peek -h")


@pytest.mark.skipif(is_ci, reason="Skip on CI")
def test_send_email():
    """Test send email."""
    assert "" == shell_run("ccbr_tools send-email -d")


def test_help_send_email():
    """Test help send email."""
    assert "Usage: ccbr_tools send-email [OPTIONS] [TO_ADDRESS] [TEXT]" in shell_run(
        "ccbr_tools send-email -h"
    )


def test_quarto_add(tmp_path):
    """Test quarto add."""
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        shell_run("ccbr_tools quarto-add fnl")
        extension_dir = pathlib.Path("_extensions") / "fnl"
        assert extension_dir.is_dir()
        assert len(os.listdir(extension_dir)) > 0
    finally:
        os.chdir(current_wd)


def test_install():
    """Test install."""
    output = shell_run("ccbr_tools install champagne v0.3.0 --hpc biowulf", check=False)
    assert "mamba activate /" in output
    assert "pip install git+https://github.com/CCBR/CHAMPAGNE.git@v0.3.0" in output
    assert "v0.3.0" in output
