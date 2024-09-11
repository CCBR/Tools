from ccbr_tools.templates import read_template


def test_read_template():
    template_str = read_template("submit_slurm.sh")
    assert all(
        [
            template_str.startswith("#!/usr/bin/env bash"),
            template_str.endswith("{RUN_COMMAND}\n"),
        ]
    )
