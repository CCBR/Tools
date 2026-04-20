import os
import pathlib
import pytest

from ccbr_tools.templates import read_template, use_template, use_quarto_ext
from ccbr_tools.pipeline.hpc import get_hpc


def test_read_template():
    template_str = read_template("submit_slurm.sh")
    assert template_str.startswith("#!/usr/bin/env bash")
    assert template_str.endswith("{RUN_COMMAND}\n")


def test_use_template(tmp_path):
    out_filepath = tmp_path / "test.sh"
    use_template(
        "submit_slurm.sh",
        output_filepath=out_filepath,
        WALLTIME="4-00:00:00",
        MEMORY="1G",
        PIPELINE="CCBR_nxf",
        MODULES="ccbrpipeliner nextflow",
        ENV_VARS="export HELLO=WORLD",
        RUN_COMMAND="nextflow run main.nf -stub",
    )
    template_str = out_filepath.read_text()
    assert '#SBATCH -J "CCBR_nxf"' in template_str
    assert "#SBATCH --time=4-00:00:00" in template_str
    assert "module load ccbrpipeliner nextflow" in template_str
    assert "export HELLO=WORLD" in template_str
    assert "nextflow run main.nf -stub" in template_str


def generate_slurm_template():
    hpc = get_hpc(debug="biowulf")
    use_template(
        "submit_slurm.sh",
        output_filepath="tests/data/templates/submit_slurm.sh",
        WALLTIME="1-00:00:00",
        MEMORY="1G",
        PIPELINE="CCBR_nxf",
        MODULES=hpc.modules["nxf"],
        ENV_VARS=hpc.env_vars,
        RUN_COMMAND="nextflow run main.nf -stub",
    )


def test_use_template_blanks(tmp_path):
    out_filepath = tmp_path / "test.sh"
    with pytest.raises(KeyError) as exc_info:
        use_template(
            "submit_slurm.sh",
            output_filepath=out_filepath,
        )
    assert str(exc_info.value) == "'MODULES'"


def test_use_quarto_ext(tmp_path):
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        use_quarto_ext("fnl")
        ext_dir = pathlib.Path("_extensions") / "fnl"
        assert ext_dir.is_dir()
        assert len(os.listdir(ext_dir)) > 1
        assert (ext_dir / "_extension.yml").is_file()
    finally:
        os.chdir(current_wd)


def test_use_quarto_ext_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        use_quarto_ext("not_a_real_extension")
    assert str(exc_info.value).startswith("not_a_real_extension does not exist")
