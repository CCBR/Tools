from ccbr_tools.pipeline.nextflow import run
from ccbr_tools.pipeline.hpc import get_hpc, Biowulf, FRCE
from ccbr_tools.shell import exec_in_context

import tempfile


def test_nextflow_basic():
    output = exec_in_context(run, "CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output


def test_nextflow_hpc():
    assert all(
        [
            "module load"
            in exec_in_context(run, "CCBR/CHAMPAGNE", debug=True, hpc=Biowulf()),
            "module load"
            in exec_in_context(run, "CCBR/CHAMPAGNE", debug=True, hpc=FRCE()),
        ]
    )


def test_nextflow_slurm():
    assert "sbatch submit_slurm.sh" in exec_in_context(
        run, "CCBR/CHAMPAGNE", debug=True, hpc=Biowulf(), mode="slurm"
    )


if __name__ == "__main__":
    print(
        exec_in_context(run, "CCBR/CHAMPAGNE", debug=True, hpc=Biowulf(), mode="slurm")
    )
