"""
Functions for singularity cache management
"""
import json
import os
import sys


def get_singularity_cachedir(output_dir=None, cache_dir=None):
    """Returns the singularity cache directory.
    If no user-provided cache directory is provided,
    the default singularity cache is in the output directory.
    """
    if not output_dir:
        output_dir = os.getcwd()
    if not cache_dir:
        cache_dir = os.path.join(output_dir, ".singularity")
    return cache_dir


def get_sif_cache_dir(hpc=None):
    sif_dir = None
    if hpc == "biowulf":
        sif_dir = "/data/CCBR_Pipeliner/SIFS"
    elif hpc == "frce":
        sif_dir = "/mnt/projects/CCBR-Pipelines/SIFs"
    return sif_dir


def image_cache(sub_args, config):
    """Adds Docker Image URIs, or SIF paths to config if singularity cache option is provided.
    If singularity cache option is provided and a local SIF does not exist, a warning is
    displayed and the image will be pulled from URI in 'config/containers/images.json'.
    @param sub_args <parser.parse_args() object>:
        Parsed arguments for run sub-command
    @params config <file>:
        Docker Image config file
    @return config <dict>:
         Updated config dictionary containing user information (username and home directory)
    """
    images = os.path.join(sub_args.output, "config", "containers", "images.json")

    # Read in config for docker image uris
    with open(images, "r") as fh:
        data = json.load(fh)
    # Check if local sif exists
    for image, uri in data["images"].items():
        if sub_args.sif_cache:
            sif = os.path.join(
                sub_args.sif_cache,
                "{}.sif".format(os.path.basename(uri).replace(":", "_")),
            )
            if not os.path.exists(sif):
                # If local sif does not exist on in cache, print warning
                # and default to pulling from URI in config/containers/images.json
                print(
                    'Warning: Local image "{}" does not exist in singularity cache'.format(
                        sif
                    ),
                    file=sys.stderr,
                )
            else:
                # Change pointer to image from Registry URI to local SIF
                data["images"][image] = sif

    config.update(data)

    return config


## copied directly from rna-seek
def check_cache(parser, cache, *args, **kwargs):
    """Check if provided SINGULARITY_CACHE is valid. Singularity caches cannot be
    shared across users (and must be owned by the user). Singularity strictly enforces
    0700 user permission on on the cache directory and will return a non-zero exitcode.
    @param parser <argparse.ArgumentParser() object>:
        Argparse parser object
    @param cache <str>:
        Singularity cache directory
    @return cache <str>:
        If singularity cache dir is valid
    """
    if not exists(cache):
        # Cache directory does not exist on filesystem
        os.makedirs(cache)
    elif os.path.isfile(cache):
        # Cache directory exists as file, raise error
        parser.error(
            """\n\t\x1b[6;37;41mFatal: Failed to provided a valid singularity cache!\x1b[0m
        The provided --singularity-cache already exists on the filesystem as a file.
        Please run {} again with a different --singularity-cache location.
        """.format(
                sys.argv[0]
            )
        )
    elif os.path.isdir(cache):
        # Provide cache exists as directory
        # Check that the user owns the child cache directory
        # May revert to os.getuid() if user id is not sufficient
        if (
            os.path.exists(os.path.join(cache, "cache"))
            and os.stat(os.path.join(cache, "cache")).st_uid != os.getuid()
        ):
            # User does NOT own the cache directory, raise error
            parser.error(
                """\n\t\x1b[6;37;41mFatal: Failed to provided a valid singularity cache!\x1b[0m
                The provided --singularity-cache already exists on the filesystem with a different owner.
                Singularity strictly enforces that the cache directory is not shared across users.
                Please run {} again with a different --singularity-cache location.
                """.format(
                    sys.argv[0]
                )
            )

    return cache
