"""
Helpers for bioinformatics pipelines

- [](`~ccbr_tools.pipeline.cache`)
- [](`~ccbr_tools.pipeline.hpc`)
- [](`~ccbr_tools.pipeline.nextflow`)
- [](`~ccbr_tools.pipeline.util`)
"""

import math
import re


class Pipeline:
    SAMPLES_PATTERN = None

    @classmethod
    def create(pipeline_name, pipelines=PIPELINES):
        return PIPELINES.get(pipeline_name.lower(), None)

    def count_samples(self, tree_str):
        """
        Count the number of samples in a pipeline run.

        Args:
            tree_str (str): The tree as a JSON string representing the pipeline run output directory (from `tree -aJ` command).
            pipeline_name (str): The name of the pipeline.

        Returns:
            int: The number of samples in the pipeline run. Returns NaN if the pipeline is not recognized.

        See Also:
            `~ccbr_tools.spooker.get_tree`: The function used to generate the tree structure.
        """
        nsamples = math.nan
        try:
            nsamples = re.findall(self.SAMPLES_PATTERN, tree_str)
        except Exception as err:
            warnings.warn(
                f"Could not determine number of samples for pipeline {pipeline_name}. See original error message below:\n{repr(err)}"
            )
        return nsamples


class RENEE(Pipeline):
    SAMPLES_PATTERN = r"Aligned.toTranscriptome.out.bam"


class XAVIER(Pipeline):
    SAMPLES_PATTERN = r".input.bam"


PIPELINES = {
    "renee": RENEE,
    "xavier": XAVIER,
}


def count_samples(tree_str, pipeline_name):
    """
    Count the number of samples in a pipeline run.

    Args:
        tree_str (str): The tree as a JSON string representing the pipeline run output directory (from `tree -aJ` command).
        pipeline_name (str): The name of the pipeline.

    Returns:
        int: The number of samples in the pipeline run. Returns NaN if the pipeline is not recognized.

    See Also:
        `~ccbr_tools.spooker.get_tree`: The function used to generate the tree structure.
    """
    nsamples = math.nan
    pipeline = Pipeline.create(pipeline_name)
    if pipeline:
        nsamples = pipeline.count_samples(tree_str)
    else:
        warnings.warn(f"Pipeline {pipeline_name} not recognized. Cannot count samples.")

    return nsamples
