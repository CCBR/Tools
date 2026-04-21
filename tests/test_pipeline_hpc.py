import io
import sys

from ccbr_tools.pipeline.hpc import get_hpc, get_hpcname
from ccbr_tools.shell import shell_run


def test_hpc_biowulf():
    hpc = get_hpc(debug="biowulf")
    assert hpc
    assert hpc.name == "biowulf"
    assert hpc.singularity_sif_dir == "/data/CCBR_Pipeliner/SIFs"
    assert hpc.__repr__().startswith(
        "<class 'ccbr_tools.pipeline.hpc.Biowulf'>({'name': 'biowulf'"
    )
    assert "mamba activate /" in hpc.CONDA_ACTIVATE


def test_hpc_frce():
    hpc = get_hpc(debug="frce")
    assert hpc
    assert hpc.name == "frce"
    assert "/mnt/projects/CCBR-Pipelines/bin" in hpc.env_vars
    assert hpc.singularity_sif_dir == "/mnt/projects/CCBR-Pipelines/SIFs"
    assert "mamba activate " in hpc.CONDA_ACTIVATE


def test_hpc_none():
    hpc = get_hpc(debug=" ")
    assert not any([hpc, hpc.name, hpc.singularity_sif_dir])


def test_hpcname_type():
    hpcname = get_hpcname()
    assert isinstance(hpcname, str), "Expected hpcname to be a string"


def test_hpcname_expected_values():
    hpcname = get_hpcname().strip().lower()
    if hpcname:
        assert hpcname in ["biowulf", "frce", "helix"], f"Unexpected hpcname: {hpcname}"


def test_hpcname_print_output():
    captured = io.StringIO()
    sys.stdout = captured
    print(get_hpcname())
    sys.stdout = sys.__stdout__

    printed = captured.getvalue().strip()
    expected = get_hpcname().strip()
    assert printed == expected, (
        f"Printed output '{printed}' != return value '{expected}'"
    )


def test_hpcname_cli():
    out = shell_run("get_hpcname", shell=True, capture_output=True, text=True).strip()
    assert not out


if __name__ == "__main__":
    print(get_hpc(debug="biowulf").__repr__())
