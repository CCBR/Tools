import os
import pathlib
import pytest
import subprocess

from ccbr_tools.pipeline.nextflow import run, init
from ccbr_tools.pipeline.hpc import Biowulf, FRCE
from ccbr_tools.shell import exec_in_context


def test_init(tmp_path, data_dir):
    init(
        output=tmp_path,
        repo_base=lambda f: data_dir / "pipeline" / f,
        pipeline_name="test_pipeline",
    )
    assert (tmp_path / "log").exists()
    assert (tmp_path / "nextflow.config").exists()
    assert (tmp_path / "conf").exists()
    assert (tmp_path / "assets").exists()


def test_nextflow_basic():
    output = exec_in_context(run, nextfile_path="CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" in output


def test_nextflow_forceall():
    output = exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, force_all=True
    )
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" not in output


def test_nextflow_hpc():
    assert "module load nextflow/25 &&" in exec_in_context(
        run,
        nextfile_path="CCBR/CHAMPAGNE",
        debug=True,
        hpc=Biowulf(),
        hpc_modules="nextflow/25",
    )
    assert "module load nextflow &&" in exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=FRCE()
    )


def test_nextflow_slurm(tmp_path):
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        out = exec_in_context(
            run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=Biowulf(), mode="slurm"
        )
        slurm_txt = (tmp_path / "submit_slurm.sh").read_text()
    finally:
        os.chdir(current_wd)
    assert "sbatch submit_slurm.sh" in out
    assert "nextflow run CCBR/CHAMPAGNE" in slurm_txt
    assert "module load nextflow" in slurm_txt
    assert '#SBATCH -J "CCBR/CHAMPAGNE"' in slurm_txt


def test_nextflow_preview_error(tmp_path, data_dir_rel):
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        with pytest.raises(subprocess.CalledProcessError) as err:
            exec_in_context(
                run,
                nextfile_path=str(data_dir_rel / "nextflow" / "main.nf"),
                debug=False,
                mode="local",
            )
    finally:
        os.chdir(current_wd)
    assert (
        f"Command 'nextflow run {data_dir_rel / 'nextflow' / 'main.nf'} -resume -preview' returned non-zero exit status 1"
        in str(err.value)
    )


if __name__ == "__main__":
    test_nextflow_slurm()
