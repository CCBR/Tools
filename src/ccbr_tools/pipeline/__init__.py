"""
Helpers for bioinformatics pipelines

- [](`~ccbr_tools.pipeline.cache`)
- [](`~ccbr_tools.pipeline.hpc`)
- [](`~ccbr_tools.pipeline.nextflow`)
- [](`~ccbr_tools.pipeline.util`)
"""

import math
import re
from ..paths import load_tree


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
    pipeline = create_pipeline(pipeline_name)
    if pipeline:
        nsamples = pipeline.count_samples(tree_str)
    else:
        warnings.warn(f"Pipeline {pipeline_name} not recognized. Cannot count samples.")
    return nsamples


class Pipeline:
    SAMPLES_PATTERN = None  # must be a regex pattern with exactly one capture group, which excludes slashes

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
            # get unique set of capture groups for all matches
            nsamples = len(set(re.findall(self.SAMPLES_PATTERN, tree_str)))
        except Exception as err:
            warnings.warn(
                f"Could not determine number of samples for pipeline {pipeline_name}. See original error message below:\n{repr(err)}"
            )
        return nsamples


class ASPEN(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*.reads.bam.bai)"'


class CARLISLE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*no_dedup.bam.bai)"'


class CHAMPAGNE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-]*filtered.sorted.bam.bai)"'


class CHARLIE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*.ciri.bam.csi)"'


class CRISPIN(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*).foldchange.txt"'


class ESCAPE(Pipeline):
    SAMPLES_PATTERN = None  # TODO


class LOGAN(Pipeline):
    SAMPLES_PATTERN = None  # TODO


class RENEE(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*Aligned.toTranscriptome.out.bam)"'


class SINCLAIR(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*seurat_preprocess.rds)"'


class XAVIER(Pipeline):
    SAMPLES_PATTERN = r'"name":"([a-zA-Z0-9_\-\.]*.input.bam)"'


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
    return pipelines.get(pipeline_name.lower(), None)
