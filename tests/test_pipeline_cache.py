from ccbr_tools.pipeline.cache import get_sif_cache_dir, get_singularity_cachedir


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
