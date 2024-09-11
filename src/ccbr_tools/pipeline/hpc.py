"""
Classes for working with different HPC clusters.

Use [](`ccbr_tools.pipeline.hpc.get_hpc`) to retrieve an HPC Cluster instance,
which contains default attributes for supported clusters.
"""

from .util import get_hpcname
from .cache import get_singularity_cachedir


class Cluster:
    """
    Base class for an HPC cluster - evaluates to None

    Attributes:
        name (str): The name of the cluster.
        modules (dict): A dictionary containing the modules installed on the cluster.
            The keys are the module names and the values are the corresponding versions.
        singularity_sif_dir (str): The directory where Singularity SIF files are stored.
        env_vars (str): A string representing the environment variables to be set on the cluster.
    """

    def __init__(self):
        self.name = None
        self.modules = {"nxf": None, "smk": None}
        self.env_vars = "\n".join(
            (f"export SINGULARITY_CACHEDIR={get_singularity_cachedir()}",)
        )
        self.singularity_sif_dir = None

    def __repr__(self):
        return f"{self.__class__}({self.__dict__})"

    def __bool__(self):
        return bool(self.name)

    __nonzero__ = __bool__


class Biowulf(Cluster):
    """
    The Biowulf cluster -- child of [](`ccbr_tools.pipeline.hpc.Cluster`)

    Attributes:
        name (str): The name of the cluster.
        modules (dict): A dictionary mapping module names to their corresponding commands.
        singularity_sif_dir (str): The directory path for Singularity SIF files.
        env_vars (str): A string representing the environment variables to be set on the cluster.
    """

    def __init__(self):
        super().__init__()
        self.name = "biowulf"
        self.modules = {
            "nxf": "ccbrpipeliner nextflow",
            "smk": "ccbrpipeliner snakemake/7 singularity",
        }
        self.singularity_sif_dir = "/data/CCBR_Pipeliner/SIFs"


class FRCE(Cluster):
    """
    The FRCE cluster -- child of [](`ccbr_tools.pipeline.hpc.Cluster`)

    Attributes:
        name (str): The name of the cluster.
        modules (dict): A dictionary mapping module names to their corresponding commands.
        singularity_sif_dir (str): The directory path for Singularity SIF files.
        env_vars (str): A string representing the environment variables to be set on the cluster.
    """

    def __init__(self):
        super().__init__()
        self.name = "frce"
        self.modules = {"nxf": "nextflow", "smk": "snakemake/7 singularity"}
        self.singularity_sif_dir = "/mnt/projects/CCBR-Pipelines/SIFs"
        self.env_vars = "\n".join(
            (
                self.env_vars,
                "export PATH=${PATH}:/mnt/projects/CCBR-Pipelines/bin",
            )
        )


def get_hpc(debug=False):
    """
    Returns an instance of the High-Performance Computing (HPC) cluster based on the specified HPC name.

    If the HPC is not known or supported, an instance of the base `Cluster` class is returned.

    Args:
        debug (bool, optional): If True, uses `debug` as the HPC name. Defaults to False.

    Returns:
        cluster (Cluster): An instance of the HPC cluster.

    Examples:
        >>> get_hpc()
        >>> get_hpc(debug=True)
    """
    hpc_options = {"biowulf": Biowulf, "frce": FRCE}
    hpc_name = get_hpcname() if not debug else debug
    return hpc_options.get(hpc_name, Cluster)()
