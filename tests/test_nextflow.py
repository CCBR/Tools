from ccbr_tools.pipeline.nextflow import run
from ccbr_tools.pipeline.hpc import get_hpc
from ccbr_tools.shell import exec_in_context


def test_nextflow_basic():
    output = exec_in_context(run, "CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output


def test_nextflow_hpc():
    hpc = get_hpc()
    if hpc.name == "biowulf" or hpc.name == "frce":
        output = exec_in_context(run, "CCBR/CHAMPAGNE", debug=True)
        assert "module load" in output
