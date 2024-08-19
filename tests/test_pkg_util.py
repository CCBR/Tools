from ccbr_tools.pkg_util import read_template


def test_read_template():
    template_str = read_template("slurm_nxf_biowulf.sh")
    assert all(
        [
            template_str.startswith("#!/usr/bin/env bash"),
            template_str.endswith("{RUN_COMMAND}"),
        ]
    )
