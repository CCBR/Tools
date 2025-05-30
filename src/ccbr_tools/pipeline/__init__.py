"""
Helpers for bioinformatics pipelines

Submodules:

- [](`~ccbr_tools.pipeline.cache`)
- [](`~ccbr_tools.pipeline.hpc`)
- [](`~ccbr_tools.pipeline.nextflow`)
- [](`~ccbr_tools.pipeline.util`)

Main classes & functions

- [](`~ccbr_tools.pipeline.count_pipeline_samples`): Count the number of samples in a pipeline run.
- [](`~ccbr_tools.pipeline.Pipeline`): Base class for all pipelines.
- [](`~ccbr_tools.pipeline.create_pipeline`): Create a pipeline object from a pipeline name.
"""

import math
import re
import warnings


def count_pipeline_samples(tree_str, pipeline_name):
    """
    Count the number of samples in a pipeline run.

    Args:
        tree_str (str): The tree as a JSON string representing the pipeline run output directory (from `tree -aJ` command).
        pipeline_name (str): The name of the pipeline.

    Returns:
        int: The number of samples in the pipeline run. Returns NaN if the pipeline is not recognized.
        list: The sample names in the pipeline run. Returns an empty list if the pipeline is not recognized.

    See Also:
        `~ccbr_tools.spooker.get_tree`: The function used to generate the tree structure.
    """
    nsamples = math.nan
    sample_names = list()
    pipeline = create_pipeline(pipeline_name)
    if pipeline:
        nsamples, sample_names = pipeline.count_samples(tree_str)
    else:
        warnings.warn(
            f"Pipeline {pipeline_name} not recognized. Cannot retrieve samples."
        )
    return nsamples, sample_names


class Pipeline:
    SAMPLES_PATTERN = None  # must be a regex pattern with exactly one capture group, which excludes slashes

    @classmethod
    def count_samples(cls, tree_str):
        """
        Count the number of samples in a pipeline run.

        Args:
            tree_str (str): The tree as a JSON string representing the pipeline run output directory (from `tree -aJ` command).
            pipeline_name (str): The name of the pipeline.

        Returns:
            int: The number of samples in the pipeline run. Returns NaN if the pipeline is not recognized.
            list: The sample names in the pipeline run. Returns an empty list if the pipeline is not recognized.
        See Also:
            `~ccbr_tools.spooker.get_tree`: The function used to generate the tree structure.
        """
        nsamples = math.nan
        sample_names = list()
        try:
            sample_names = cls.get_samples(tree_str)
            nsamples = len(sample_names)
        except Exception as err:
            warnings.warn(
                f"Could not determine number of samples. See original error message below:\n{repr(err)}"
            )
        return nsamples, sample_names

    @classmethod
    def get_samples(cls, tree_str):
        """
        Get the sample names in a pipeline run.

        Args:
            tree_str (str): The tree as a JSON string representing the pipeline run output directory (from `tree -aJ` command).

        Returns:
            list: unique sample names

        See Also:
            `~ccbr_tools.spooker.get_tree`: The function used to generate the tree structure.
        """
        # get unique set of capture groups for all matches
        return sorted(set(re.findall(cls.SAMPLES_PATTERN, tree_str)))


class ASPEN(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).reads.bam.bai"'


class CARLISLE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).no_dedup.bam.bai"'


class CHAMPAGNE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).filtered.sorted.bam.bai"'


class CHARLIE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).ciri.bam.csi"'


class CRISPIN(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).foldchange.txt"'


class ESCAPE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).Aligned.out.filtered.bam"'


class LOGAN(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).bqsr.bam.bai"'


class RENEE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).Aligned.toTranscriptome.out.bam"'


class SINCLAIR(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*)seurat_preprocess.rds"'


class XAVIER(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).input.bam"'


PIPELINES = {
    "aspen": ASPEN,
    "carlisle": CARLISLE,
    "champagne": CHAMPAGNE,
    "charlie": CHARLIE,
    "crispin": CRISPIN,
    "escape": ESCAPE,
    "logan": LOGAN,
    "renee": RENEE,
    "sinclair": SINCLAIR,
    "xavier": XAVIER,
}


def create_pipeline(pipeline_name, pipelines=PIPELINES):
    """
    Retrieves a pipeline class by its name from the provided pipelines dictionary.
    Args:
        pipeline_name (str): The name of the pipeline to retrieve.
        pipelines (dict, optional): A dictionary mapping pipeline names to pipeline functions or objects.
            Defaults to PIPELINES.
    Returns:
        object or None: The pipeline class if found; otherwise, None.
    """
    return pipelines.get(pipeline_name.lower(), None)
