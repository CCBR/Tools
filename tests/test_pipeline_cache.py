import argparse

from ccbr_tools.pipeline.cache import (
    get_sif_cache_dir,
    get_singularity_cachedir,
    image_cache,
    check_cache,
)


def test_get_sif_cache_dir():
    assert "CCBR_Pipeliner/SIFs" in get_sif_cache_dir("biowulf")
    assert "CCBR-Pipelines/SIFs" in get_sif_cache_dir("frce")


def test_get_singularity_cachedir():
    assert get_singularity_cachedir("outdir") == "outdir/.singularity"
    assert get_singularity_cachedir("outdir", "cache") == "cache"


def test_image_cache(data_dir_rel):
    d = image_cache(
        argparse.Namespace(
            output=str(data_dir_rel), sif_cache=str(data_dir_rel / "sif")
        ),
        config=dict(),
    )
    assert "images" in d
    assert list(d["images"].values())[0].startswith("docker://")


def test_check_cache(tmp_path, data_dir_rel):
    sif_dir = tmp_path / "sifs"
    assert check_cache(argparse.Namespace(), sif_dir) == sif_dir
    assert check_cache(argparse.Namespace(), str(data_dir_rel / "sifs")) == str(
        data_dir_rel / "sifs"
    )
