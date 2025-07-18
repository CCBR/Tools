"""
Classes for working with different HPC clusters.

Use [](`~ccbr_tools.pipeline.hpc.get_hpc`) to retrieve an HPC Cluster instance,
which contains default attributes for supported clusters.
"""

import pathlib
import re
import shutil
import subprocess

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

    def spook(self, file, subdir=None):
        dest_dir = self.SPOOK_DIR / subdir if subdir else self.SPOOK_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, dest_dir)
        return dest_dir / file.name

    @property
    def singularity_sif_dir(self):
        return get_sif_cache_dir(hpc=self.name)

    @staticmethod
    def create_hpc(debug=False):
        hpc_options = {
            "biowulf": Biowulf,
            "frce": FRCE,
            "gha": GitHubActions,
            "unknown": Cluster,
        }
        hpc_name = get_hpcname() if not debug else debug
        return hpc_options.get(hpc_name, Cluster)()


class Biowulf(Cluster):
    """
    The Biowulf cluster -- child of [](`~ccbr_tools.pipeline.hpc.Cluster`)

    Attributes:
        name (str): The name of the cluster.
        modules (dict): A dictionary mapping module names to their corresponding commands.
        singularity_sif_dir (str): The directory path for Singularity SIF files.
        env_vars (str): A string representing the environment variables to be set on the cluster.
    """

    GROUP = "CCBR_Pipeliner"
    PIPELINES_HOME = pathlib.Path("/data/CCBR_Pipeliner/Pipelines")
    TOOLS_HOME = pathlib.Path("/data/CCBR_Pipeliner/Tools")
    CONDA_ACTIVATE = ". '/data/CCBR_Pipeliner/db/PipeDB/Conda2025/etc/profile.d/conda.sh' && conda activate /data/CCBR_Pipeliner/db/PipeDB/Conda2025/envs/py3.11-8"
    SPOOK_DIR = pathlib.Path("/data/CCBR_Pipeliner/userdata_staging")

    def __init__(self):
        super().__init__()
        self.name = "biowulf"
        self.env_vars = "\n".join(
            (
                f"export SINGULARITY_CACHEDIR={get_singularity_cachedir()}",
                'if ! command -v spooker 2>&1 >/dev/null; then export PATH="$PATH:/data/CCBR_Pipeliner/Tools/ccbr_tools/v0.4/bin/"; fi',
            )
        )

    # def spook(self, file, subdir=None):
    #     dest_dir = self.SPOOK_DIR / subdir if subdir else self.SPOOK_DIR
    #     dest_dir.mkdir(parents=True, exist_ok=True)
    #     outfile = dest_dir / file.name
    #     try:
    #         shell_run(f"spook -f {file} -d {dest_dir} --nosubfolder", capture_output=False)
    #     except subprocess.CalledProcessError as err:
    #         outfile = super().spook(file, subdir=subdir)
    #         warnings.warn(f"Error running spook, copying file instead. Original error: {repr(err)}")
    #     return outfile


class FRCE(Cluster):
    """
    The FRCE cluster -- child of [](`~ccbr_tools.pipeline.hpc.Cluster`)

    Attributes:
        name (str): The name of the cluster.
        modules (dict): A dictionary mapping module names to their corresponding commands.
        singularity_sif_dir (str): The directory path for Singularity SIF files.
        env_vars (str): A string representing the environment variables to be set on the cluster.
    """

    GROUP = "nci-frederick-ccbr-pipelines"
    PIPELINES_HOME = pathlib.Path("/mnt/projects/CCBR-Pipelines/pipelines")
    TOOLS_HOME = pathlib.Path("/mnt/projects/CCBR-Pipelines/tools")
    CONDA_ACTIVATE = ". '/mnt/projects/CCBR-Pipelines/resources/miniconda3/etc/profile.d/conda.sh' && conda activate py311"
    SPOOK_DIR = pathlib.Path(
        "/mnt/projects/CCBR-Pipelines/pipelines/userdata/ccbrpipeliner"
    )

    def __init__(self):
        super().__init__()
        self.name = "frce"
        self.env_vars = "\n".join(
            (
                self.env_vars,
                "export PATH=${PATH}:/mnt/projects/CCBR-Pipelines/bin",
            )
        )


class GitHubActions(Cluster):
    SPOOK_DIR = pathlib.Path("tests/data/spooker")

    def __init__(self):
        super().__init__()
        self.name = "gha"


def get_hpc(debug=False):
    """
    Returns an instance of the High-Performance Computing (HPC) cluster based on the specified HPC name.

    If the HPC is not known or supported, an instance of the base `Cluster` class is returned.

    Args:
        debug (bool, optional): If True, uses `debug` as the HPC name. Defaults to False.

    Returns:
        cluster (Cluster): An instance of the HPC cluster.

    See Also:
        `~ccbr_tools.pipeline.hpc.Cluster.create_hpc`: The base class for HPC clusters.

    Examples:
        >>> get_hpc()
        >>> get_hpc(debug=True)
    """
    return Cluster.create_hpc(debug=debug)


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
    if not hpc:  # check hostname
        hostname = shell_run("hostname", shell=True, capture_output=True, text=True)
        if "helix" in hostname:
            hpc = "helix"
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


def list_modules():
    """
    Get the list of loaded modules using `module list`

    Returns:
        loaded_modules (str): The output of `module list`
    """
    return shell_run("bash -c 'module list'", check=False)


def parse_modules(ml_output):
    """
    Parse the output of `module list` to extract module names and versions
    Args:
        ml_output (str): The output of `module list`
    Returns:
        modules (dict): A dictionary containing module names and their versions
    Example:
        >>> ml_output = "1) module_name/version"
        >>> parse_modules(ml_output)
        {'module_name': 'version'}
        >>> parse_modules(list_modules())
        {'module_name': 'version', ...}
    """
    modules = {}
    # Pattern to match entries like:
    # 1) snakemake/7 -> snakemake/7.32.4
    # 2) ccbrpipeliner/8
    pattern = re.compile(r"\d+\)\s+([\w\-]+)/([\w\-.]+)(?:\s+->\s+[\w\-]+/([\w\-.]+))?")

    for match in pattern.finditer(ml_output):
        name = match.group(1)
        short_version = match.group(2)
        resolved_version = match.group(3)
        modules[name] = resolved_version if resolved_version else short_version

    return modules


def is_loaded(module="ccbrpipeliner"):
    """
    Check whether a module is loaded

    Args:
        module (str): The name of the module to check (default: "ccbrpipeliner")

    Returns:
        is_loaded (bool): True if the module is loaded, False otherwise
    """
    return module in list_modules()


def main():
    HPC = get_hpcname()
    print(f"{HPC}")


if __name__ == "__main__":
    main()
