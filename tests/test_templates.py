import pathlib
import tempfile

from ccbr_tools.templates import read_template, use_template


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
        out_filepath = pathlib.Path(tmp_dir) / "submit_slurm.sh"
        use_template(
            "submit_slurm.sh",
            output_filepath=out_filepath,
            PIPELINE="CCBR_nxf",
            MODULES="ccbrpipeliner nextflow",
            ENV_VARS="export HELLO=WORLD",
            RUN_COMMAND="nextflow run main.nf -stub",
        )
        with open(out_filepath, "r") as outfile:
            template_str = outfile.read()
            print(template_str)
    assert all(
        [
            '#SBATCH -J "CCBR_nxf"' in template_str,
            "module load ccbrpipeliner nextflow" in template_str,
            "export HELLO=WORLD" in template_str,
            "nextflow run main.nf -stub" in template_str,
        ]
    )
