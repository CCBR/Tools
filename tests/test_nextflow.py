import os
import pathlib
import tempfile

from ccbr_tools.pipeline.nextflow import run, init
from ccbr_tools.pipeline.hpc import Biowulf, FRCE, get_hpc
from ccbr_tools.shell import exec_in_context


def test_init():
    with tempfile.TemporaryDirectory() as tmp_dir:
        init(
            output=tmp_dir,
            repo_base=lambda f: pathlib.Path(__file__).absolute().parent
            / "data"
            / "pipeline"
            / f,
            pipeline_name="test_pipeline",
        )
        assert all(
            [
                (pathlib.Path(tmp_dir) / "log/").exists(),
                (pathlib.Path(tmp_dir) / "nextflow.config").exists(),
                (pathlib.Path(tmp_dir) / "conf/").exists(),
                (pathlib.Path(tmp_dir) / "assets/").exists(),
            ]
        )


def test_nextflow_basic():
    output = exec_in_context(run, nextfile_path="CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" in output


def test_nextflow_forceall():
    output = exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, force_all=True
    )
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" not in output


def test_nextflow_hpc():
    assert all(
        [
            "module load"
            in exec_in_context(
                run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=Biowulf()
            ),
            "module load"
            in exec_in_context(
                run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=FRCE()
            ),
        ]
    )


def test_nextflow_slurm():
    with tempfile.TemporaryDirectory() as tmp_dir:
        current_wd = os.getcwd()
        os.chdir(tmp_dir)
        out = exec_in_context(
            run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=Biowulf(), mode="slurm"
        )
        with open(pathlib.Path(tmp_dir) / "submit_slurm.sh", "r") as slurm_file:
            slurm_txt = slurm_file.read()

        os.chdir(current_wd)
        assert all(
            [
                "sbatch submit_slurm.sh" in out,
                "nextflow run CCBR/CHAMPAGNE" in slurm_txt,
                "module load nextflow" in slurm_txt,
                '#SBATCH -J "CCBR/CHAMPAGNE"' in slurm_txt,
            ]
        )


if __name__ == "__main__":
    test_nextflow_slurm()
