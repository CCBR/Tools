import argparse
import pathlib
import tempfile

from ccbr_tools.pipeline.cache import (
    get_sif_cache_dir,
    get_singularity_cachedir,
    image_cache,
    check_cache,
)


def test_get_sif_cache_dir():
    assertions = [
        "'CCBR_Pipeliner/SIFs' in get_sif_cache_dir('biowulf')",
        "'CCBR-Pipelines/SIFs' in get_sif_cache_dir('frce')",
    ]
    errors = [assertion for assertion in assertions if not eval(assertion)]
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))


def test_get_singularity_cachedir():
    assertions = [
        "get_singularity_cachedir('outdir') == 'outdir/.singularity'",
        "get_singularity_cachedir('outdir', 'cache') == 'cache'",
    ]
    errors = [assertion for assertion in assertions if not eval(assertion)]
    assert not errors, "errors occurred:\n{}".format("\n".join(errors))


def test_image_cache():
    d = image_cache(
        argparse.Namespace(output="tests/data", sif_cache="tests/data/sif/"),
        config=dict(),
    )
    assertions = ["images" in d, list(d["images"].values())[0].startswith("docker://")]
    assert all(assertions)


def test_check_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        sif_dir = pathlib.Path(tmpdir) / "sifs"
        assert all(
            [
                check_cache(argparse.Namespace(), sif_dir) == sif_dir,
                check_cache(argparse.Namespace(), "tests/data/sifs")
                == "tests/data/sifs",
            ]
        )
