from ccbr_tools.pipeline.hpc import get_hpc


def test_hpc_biowulf():
    hpc = get_hpc(debug="biowulf")
    assert all(
        [
            hpc,
            hpc.name == "biowulf",
            hpc.singularity_sif_dir == "/data/CCBR_Pipeliner/SIFs",
            hpc.__repr__().startswith(
                "<class 'ccbr_tools.pipeline.hpc.Biowulf'>({'name': 'biowulf'"
            ),
            "conda.sh' && conda activate /" in hpc.CONDA_ACTIVATE,
        ]
    )


def test_hpc_frce():
    hpc = get_hpc(debug="frce")
    assert all(
        [
            hpc,
            hpc.name == "frce",
            "/mnt/projects/CCBR-Pipelines/bin" in hpc.env_vars,
            hpc.singularity_sif_dir == "/mnt/projects/CCBR-Pipelines/SIFs",
            "conda.sh' && conda activate " in hpc.CONDA_ACTIVATE,
        ]
    )


def test_hpc_none():
    hpc = get_hpc(debug=" ")
    assert not any([hpc, hpc.name, *hpc.modules.values(), hpc.singularity_sif_dir])


if __name__ == "__main__":
    print(get_hpc(debug="biowulf").__repr__())
