from ccbr_tools.shell import shell_run

import os
import pathlib
import tempfile


def test_version_flag():
    assert "ccbr_tools, version " in shell_run("ccbr_tools -v")


def test_version_cmd():
    assert "VERSION file path" in shell_run("ccbr_tools version --debug")


def test_help():
    assert "Utilities for CCBR Bioinformatics Software" in shell_run("ccbr_tools -h")


def test_help_cite():
    assert "Print the citation in the desired format" in shell_run("ccbr_tools cite -h")


def test_help_gb2gtf():
    assert "Usage: gb2gtf sequence.gb > sequence.gtf" in shell_run("gb2gtf -h")


def test_help_hf():
    assert "Get Human2Mouse (or Mouse2Human) homolog gene or genelist" in shell_run(
        "hf -h"
    )


def test_help_jobby():
    assert "jobby <jobid1> [jobid2 ...] " in shell_run("jobby -h")


def test_help_jobinfo():
    jobinfo_help = shell_run("jobinfo -h")
    assert (
        "Get HPC usage metadata for a list of slurm jobids on biowulf" in jobinfo_help
    )


def test_help_intersect():
    assert "intersect filename1 filename2 f1ColumnIndex F2ColumnIndex" in shell_run(
        "intersect -h"
    )


def test_help_peek():
    assert "USAGE: peek <file.tsv> [buffer]" in shell_run("peek -h")


def test_send_email():
    assert "" == shell_run("ccbr_tools send-email -d")


def test_help_send_email():
    assert "Usage: ccbr_tools send-email [OPTIONS] [TO_ADDRESS] [TEXT]" in shell_run(
        "ccbr_tools send-email -h"
    )


def test_quarto_add():
    with tempfile.TemporaryDirectory() as tmp_dir:
        current_wd = os.getcwd()
        os.chdir(tmp_dir)
        shell_run("ccbr_tools quarto-add fnl")
        assertions = [
            (pathlib.Path("_extensions") / "fnl").is_dir(),
            len(os.listdir(pathlib.Path("_extensions") / "fnl")) > 0,
        ]
        os.chdir(current_wd)
    assert all(assertions)


def test_install():
    output = shell_run("ccbr_tools install champagne v0.3.0 --hpc biowulf", check=False)
    assert (
        output
        == """conda activate /data/CCBR_Pipeliner/db/PipeDB/Conda/envs/py311
pip install git+https://github.com/CCBR/CHAMPAGNE.git@v0.3.0 -t /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0
chmod -R a+rX /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0
chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0
pushd /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE
rm -if v0.3
ln -s .v0.3.0 v0.3
popd
"""
    )
