from ccbr_tools.pipeline.nextflow import run
from ccbr_tools.shell import exec_in_context


def test_nextflow_basic():
    assert "nextflow run CCBR/CHAMPAGNE" in exec_in_context(
        run, "CCBR/CHAMPAGNE", debug=True
    )
