import os
import pathlib
import subprocess

import pytest

from ccbr_tools.pipeline.hpc import FRCE, Biowulf
from ccbr_tools.pipeline.nextflow import init, run
from ccbr_tools.shell import exec_in_context


def test_init(tmp_path, data_dir):
    """Test init."""
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
    """Test nextflow basic."""
    output = exec_in_context(run, nextfile_path="CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" in output


def test_nextflow_forceall():
    """Test nextflow forceall."""
    output = exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, force_all=True
    )
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" not in output


def test_nextflow_hpc():
    """Test nextflow hpc."""
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
    """Test nextflow slurm."""
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
    """Test nextflow preview error."""
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


def test_nextflow_env_vars_local():
    """Test env_vars in local mode."""
    env_vars = ["export VAR1=value1", "export VAR2=value2"]
    output = exec_in_context(
        run,
        nextfile_path="CCBR/CHAMPAGNE",
        debug=True,
        mode="local",
        env_vars=env_vars,
    )
    assert "export VAR1=value1" in output
    assert "export VAR2=value2" in output
    assert "nextflow run CCBR/CHAMPAGNE" in output


def test_nextflow_env_vars_hpc_local():
    """Test env_vars in local mode with HPC."""
    env_vars = ["export NXF_VER=25.10.0", "export NXF_JAVA_OPTS=-Xmx2g"]
    output = exec_in_context(
        run,
        nextfile_path="CCBR/CHAMPAGNE",
        debug=True,
        mode="local",
        hpc=Biowulf(),
        hpc_modules="nextflow/25",
        env_vars=env_vars,
    )
    assert "module load nextflow/25" in output
    assert "export NXF_VER=25.10.0" in output
    assert "export NXF_JAVA_OPTS=-Xmx2g" in output
    assert "nextflow run CCBR/CHAMPAGNE" in output


def test_nextflow_env_vars_slurm(tmp_path):
    """Test env_vars in SLURM mode."""
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        env_vars = ["export NXF_VER=25.10.0", "export NXF_JAVA_OPTS=-Xmx4g"]
        out = exec_in_context(
            run,
            nextfile_path="CCBR/CHAMPAGNE",
            debug=True,
            hpc=Biowulf(),
            mode="slurm",
            env_vars=env_vars,
        )
        slurm_txt = (tmp_path / "submit_slurm.sh").read_text()
    finally:
        os.chdir(current_wd)
    assert "sbatch submit_slurm.sh" in out
    assert "export NXF_VER=25.10.0" in slurm_txt
    assert "export NXF_JAVA_OPTS=-Xmx4g" in slurm_txt
    assert "nextflow run CCBR/CHAMPAGNE" in slurm_txt


def test_nextflow_env_vars_empty():
    """Test that None env_vars defaults to empty list."""
    output = exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, env_vars=None
    )
    assert "nextflow run CCBR/CHAMPAGNE" in output


def test_nextflow_env_vars_multiple():
    """Test multiple env_vars are properly joined."""
    env_vars = [
        "export VAR1=value1",
        "export VAR2=value2",
        "export VAR3=value3",
    ]
    output = exec_in_context(
        run,
        nextfile_path="CCBR/CHAMPAGNE",
        debug=True,
        mode="local",
        env_vars=env_vars,
    )
    # All vars should be in the output
    for var in env_vars:
        assert var in output
    # They should be joined with &&
    assert "export VAR1=value1 && export VAR2=value2 && export VAR3=value3" in output


if __name__ == "__main__":
    test_nextflow_slurm()
