"""
Classes for working with different HPC clusters.

Use [](`~ccbr_tools.pipeline.hpc.get_hpc`) to retrieve an HPC Cluster instance,
which contains default attributes for supported clusters.
"""

from .cache import get_singularity_cachedir, get_sif_cache_dir
from ..shell import shell_run


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

    def __repr__(self):
        dict_with_props = dict(
            self.__dict__, singularity_sif_dir=self.singularity_sif_dir
        )
        return f"{self.__class__}({dict_with_props})"

    def __bool__(self):
        return bool(self.name)

    __nonzero__ = __bool__

    @property
    def singularity_sif_dir(self):
        return get_sif_cache_dir(hpc=self.name)


class Biowulf(Cluster):
    """
    The Biowulf cluster -- child of [](`~ccbr_tools.pipeline.hpc.Cluster`)

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
            "nxf": " ".join(
                [
                    "nextflow",
                    "" if is_loaded(module="ccbrpipeliner") else "ccbrpipeliner",
                ]
            ),
            "smk": " ".join(
                [
                    "snakemake/7",
                    "singularity",
                    "" if is_loaded(module="ccbrpipeliner") else " ccbrpipeliner",
                ]
            ),
        }


class FRCE(Cluster):
    """
    The FRCE cluster -- child of [](`~ccbr_tools.pipeline.hpc.Cluster`)

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


def get_hpcname():
    """
    Get the HPC name using scontrol

    Returns:
        hpcname (str): The HPC name  (biowulf, frce, or an empty string)
    """
    scontrol_out = scontrol_show()
    hpc = scontrol_out["ClusterName"] if "ClusterName" in scontrol_out.keys() else ""
    if hpc == "fnlcr":
        hpc = "frce"
    return hpc


def scontrol_show():
    """
    Run `scontrol show config` and parse the output as a dictionary

    Returns:
        scontrol_dict (dict): dictionary containing the output of `scontrol show config`
    """
    scontrol_dict = dict()
    scontrol_out = shell_run(
        "scontrol show config", shell=True, capture_output=True, text=True, check=False
    )
    if len(scontrol_out) > 0:
        for line in scontrol_out.split("\n"):
            line_split = line.split("=")
            if len(line_split) > 1:
                scontrol_dict[line_split[0].strip()] = line_split[1].strip()
    return scontrol_dict


def is_loaded(module="ccbrpipeliner"):
    """
    Check whether the ccbrpipeliner module is loaded

    Returns:
        is_loaded (bool): True if the module is loaded, False otherwise
    """
    output = shell_run("bash -c 'module list'", check=False)
    return module in output
