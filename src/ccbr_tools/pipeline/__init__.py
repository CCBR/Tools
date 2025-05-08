"""
Helpers for bioinformatics pipelines

- [](`~ccbr_tools.pipeline.cache`)
- [](`~ccbr_tools.pipeline.hpc`)
- [](`~ccbr_tools.pipeline.nextflow`)
- [](`~ccbr_tools.pipeline.util`)
"""

import math

PIPELINES = {
    "renee": lambda tree: len(
        [
            f
            for f in next(
                item for item in tree[0]["contents"] if item["name"] == "bams"
            )["contents"]
            if f["name"].endswith("Aligned.toTranscriptome.out.bam")
        ]
    ),
    "xavier": lambda tree: len(
        [
            f
            for f in next(
                item
                for item in next(
                    item
                    for item in tree[0]["contents"]
                    if item["name"] == "input_files"
                )["contents"]
                if item["name"] == "bam"
            )["contents"]
            if f["name"].endswith(".bam")
        ]
    ),
}


def count_samples(tree_json, pipeline_name):
    """
    Count the number of samples in a pipeline run.

    Args:
        tree_json (dict): The JSON object representing the pipeline run.
        pipeline_name (str): The name of the pipeline.

    Returns:
        int: The number of samples in the pipeline run. Returns NaN if the pipeline is not recognized.
    """
    nsamples = math.nan
    try:
        nsamples = PIPELINES.get(pipeline_name.lower(), lambda x: math.nan)(tree_json)
    except Exception as err:
        warnings.warn(
            f"Could not determine number of samples for pipeline {pipeline_name}. See original error message below:\n{repr(err)}"
        )
    return nsamples
