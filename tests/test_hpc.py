from ccbr_tools.pipeline.hpc import get_hpc


def test_hpc_biowulf():
    hpc = get_hpc(debug="biowulf")
    assert all(
        [
            hpc,
            hpc.name == "biowulf",
            hpc.slurm_script
            == {"nxf": "slurm_nxf_biowulf.sh", "smk": "slurm_smk_biowulf.sh"},
            hpc.singularity_sif_dir == "/data/CCBR_Pipeliner/SIFs",
        ]
    )


def test_hpc_frce():
    hpc = get_hpc(debug="frce")
    assert all(
        [
            hpc,
            hpc.name == "frce",
            hpc.slurm_script
            == {"nxf": "slurm_nxf_frce.sh", "smk": "slurm_smk_frce.sh"},
            hpc.singularity_sif_dir == "/mnt/projects/CCBR-Pipelines/SIFs",
        ]
    )


def test_hpc_none():
    hpc = get_hpc(debug="")
    assert not any([hpc, hpc.name, *hpc.slurm_script.values(), hpc.singularity_sif_dir])
