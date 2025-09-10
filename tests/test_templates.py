import os
import pathlib
import pytest
import tempfile

from ccbr_tools.templates import read_template, use_template, use_quarto_ext
from ccbr_tools.pipeline.hpc import get_hpc


def test_read_template():
    template_str = read_template("submit_slurm.sh")
    assert all(
        [
            template_str.startswith("#!/usr/bin/env bash"),
            template_str.endswith("{RUN_COMMAND}\n"),
        ]
    )


def test_use_template():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_filepath = pathlib.Path(tmp_dir) / "test.sh"
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
        with open(out_filepath, "r") as outfile:
            template_str = outfile.read()
        assertions = [
            '#SBATCH -J "CCBR_nxf"' in template_str,
            "#SBATCH --time=4-00:00:00" in template_str,
            "module load ccbrpipeliner nextflow" in template_str,
            "export HELLO=WORLD" in template_str,
            "nextflow run main.nf -stub" in template_str,
        ]
    assert all(assertions)


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


def test_use_template_blanks():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_filepath = pathlib.Path(tmp_dir) / "test.sh"
        with pytest.raises(KeyError) as exc_info:
            use_template(
                "submit_slurm.sh",
                output_filepath=out_filepath,
            )
            assert str(exc_info.value) == "KeyError: 'MODULES'"


def test_use_quarto_ext():
    with tempfile.TemporaryDirectory() as tmp_dir:
        current_wd = os.getcwd()
        os.chdir(tmp_dir)
        use_quarto_ext("fnl")
        assertions = [
            (pathlib.Path("_extensions") / "fnl").is_dir(),
            len(os.listdir(pathlib.Path("_extensions") / "fnl")) > 1,
            (pathlib.Path("_extensions") / "fnl" / "_extension.yml").is_file(),
        ]
        os.chdir(current_wd)
    assert all(assertions)


def test_use_quarto_ext_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        use_quarto_ext("not_a_real_extension")
    assert str(exc_info.value).startswith("not_a_real_extension does not exist")
