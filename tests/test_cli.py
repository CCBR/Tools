from ccbr_tools.shell import shell_run
from ccbr_tools.pipeline.hpc import get_hpcname


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
    assert "Will take your job(s)... and display their information!" in shell_run(
        "jobby -h"
    )


def test_help_jobinfo():
    hpc = get_hpcname()
    jobinfo_help = shell_run("jobinfo -h")
    if hpc != "biowulf":
        assert "This script only works on BIOWULF!" in jobinfo_help
    else:
        assert (
            "Get slurm job information using slurm job id or snakemake.log file"
            in jobinfo_help
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
