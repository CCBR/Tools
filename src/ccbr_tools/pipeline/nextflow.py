"""
Run Nextflow workflows in local and HPC environments.

Functions:
- init(output, pipeline_name='pipeline', **kwargs)
    Initialize the launch directory by copying the system default config files.
- run(nextfile_path, mode="local", **kwargs)
    Run a Nextflow workflow.
"""

import os
import pathlib
import re
import shlex
import subprocess
from collections.abc import Mapping, Sequence

from ..pkg_util import msg_box
from ..templates import use_template
from .hpc import Cluster, get_hpc
from .util import copy_config


def init(output, repo_base, pipeline_name="pipeline"):
    """Initialize the launch directory by copying the system default config files"""
    output_dir = output if isinstance(output, pathlib.Path) else pathlib.Path(output)
    msg_box(f"Initializing {pipeline_name} in {output_dir}")
    (output_dir / "log/").mkdir(parents=True, exist_ok=True)
    paths = ("nextflow.config", "conf/", "assets/")
    copy_config(paths, repo_base=repo_base, outdir=output_dir)


def _prepare_args(
    args: Sequence[str], mode: str, force_all: bool, hpc: Cluster | None
) -> list[str]:
    """Merge launcher-managed flags without re-parsing other argument values."""
    profiles = set()
    forwarded = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "-profile" or arg.startswith("-profile="):
            if "=" in arg:
                value = arg.split("=", 1)[1]
            else:
                index += 1
                value = args[index] if index < len(args) else ""
            if not value or value.startswith("-") or not all(value.split(",")):
                raise ValueError("-profile requires a non-empty profile list")
            profiles.update(value.split(","))
        elif force_all and (arg == "-resume" or arg.startswith("-resume=")):
            if (
                arg == "-resume"
                and index + 1 < len(args)
                and not args[index + 1].startswith("-")
            ):
                index += 1
        else:
            forwarded.append(arg)
        index += 1
    if mode == "slurm":
        profiles.add("slurm")
    if hpc:
        profiles.add(hpc.name)
    if not force_all and not any(
        arg == "-resume" or arg.startswith("-resume=") for arg in forwarded
    ):
        forwarded.append("-resume")
    if profiles:
        forwarded.extend(["-profile", ",".join(sorted(profiles))])
    return forwarded


def run(
    nextfile_path: str | os.PathLike[str],
    mode: str = "local",
    force_all: bool = False,
    pipeline_name: str | None = None,
    nextflow_args: Sequence[str] | None = None,
    debug: bool = False,
    hpc: Cluster | None = None,
    hpc_modules: str = "nextflow",
    hpc_walltime: str = "1-00:00:00",
    hpc_memory: str = "1G",
    *,
    cwd: str | os.PathLike[str] | None = None,
    preview: bool = True,
    wait: bool = False,
    hpc_partition: str | None = None,
    env: Mapping[str, str] | None = None,
) -> None:
    """
    Runs a Nextflow workflow with support for local or SLURM (HPC) execution modes.

    Args:
        nextfile_path (str): Path to the Nextflow workflow file (main.nf), or GitHub repo (CCBR/CHAMPAGNE).
        mode (str, optional): Execution mode, either "local" or "slurm". Defaults to "local".
        force_all (bool, optional): If True, disables the Nextflow '-resume' flag to force all processes to rerun. Defaults to False.
        pipeline_name (str, optional): Name of the pipeline for reporting/logging. Defaults to None.
        nextflow_args (list, optional): Additional command-line arguments for Nextflow. Defaults to None.
        debug (bool, optional): If True, prints commands without executing them. Defaults to False.
        hpc (object, optional): HPC environment object, used for SLURM execution and module loading. Defaults to result of `~ccbr_tools.pipeline.hpc.get_hpc()`.
        hpc_modules (str, optional): Name(s) of modules to load for Nextflow execution on HPC. Defaults to "nextflow".
        hpc_walltime (str, optional): Walltime for SLURM job submission. Defaults to "1-00:00:00".
        hpc_memory (str, optional): Memory allocation for SLURM job submission. Defaults to "1G".
        cwd (path-like, optional): Launch directory, without changing the caller's working directory.
        preview (bool, optional): Run an automatic preview before execution. Defaults to True.
            An explicit '-preview' always runs locally, including in SLURM mode.
        wait (bool, optional): Wait for the SLURM driver job to finish. Defaults to False.
        hpc_partition (str, optional): SLURM partition for the driver job.
        env (mapping, optional): Environment variable overrides, applied after cluster defaults
            to previews, local execution, and the SLURM driver without changing os.environ.

    Behavior:
        - Constructs the Nextflow command with appropriate arguments and profiles.
        - Adds or removes the '-resume' flag based on force_all.
        - For SLURM mode, generates a SLURM submission script and submits it via sbatch.
        - For local mode, optionally loads modules and environment variables before running Nextflow.
        - Shows a preview of the pipeline execution before running.
        - Supports generic SLURM clusters without requiring a recognized HPC environment.
        - Preserves argument boundaries, repeated options, and values beginning with '-'.
        - Raises subprocess.CalledProcessError for preview, execution, or submission failure.
        - Executes the constructed command (unless debug is True).

    See also:
        - `~ccbr_tools.pipeline.hpc.get_hpc`: Retrieves the HPC environment object.
        - `~ccbr_tools.templates.use_template`: Generates files from templates.
    """
    if mode not in {"local", "slurm"}:
        raise ValueError(f"mode {mode} not recognized")
    nextfile_path = os.fspath(nextfile_path)
    launch_dir = pathlib.Path(cwd) if cwd is not None else pathlib.Path.cwd()
    if hpc is None:
        hpc = get_hpc()
    if not pipeline_name:
        pipeline_name = "CCBR-nxf" if nextfile_path.endswith(".nf") else nextfile_path
    args = _prepare_args(nextflow_args or (), mode, force_all, hpc)
    nextflow_command = shlex.join(["nextflow", "run", nextfile_path, *args])
    module_command = (
        f"module load {shlex.join(shlex.split(hpc_modules))}"
        if hpc and hpc_modules
        else ":"
    )
    environment = hpc.env_vars if hpc else ""
    for key, value in (env or {}).items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"Invalid environment variable name: {key!r}")
        environment += f"\nexport {key}={shlex.quote(value)}"
    setup = f"set -euo pipefail\n{module_command}\n{environment}\n"
    explicit_preview = "-preview" in args
    if preview and not explicit_preview:
        preview_command = nextflow_command + " -preview"
        msg_box("Pipeline Preview", errmsg=preview_command)
        if not debug:
            subprocess.run(
                ["bash", "-c", setup + preview_command], cwd=launch_dir, check=True
            )

    if mode == "slurm" and not explicit_preview:
        slurm_filename = "submit_slurm.sh"
        (launch_dir / "log").mkdir(exist_ok=True)
        use_template(
            slurm_filename,
            output_filepath=launch_dir / slurm_filename,
            MEMORY=hpc_memory,
            WALLTIME=hpc_walltime,
            PIPELINE=pipeline_name,
            MODULES=shlex.join(shlex.split(hpc_modules)) if hpc else "",
            ENV_VARS=environment,
            RUN_COMMAND=nextflow_command,
        )
        run_command = ["sbatch"]
        if wait:
            run_command.append("--wait")
        if hpc_partition:
            run_command.append(f"--partition={hpc_partition}")
        run_command.append(slurm_filename)
        msg_box("Slurm batch job", errmsg=shlex.join(run_command))
    else:
        run_command = ["bash", "-c", setup + nextflow_command]

    msg_box("Nextflow command", errmsg=nextflow_command)
    if not debug:
        subprocess.run(run_command, cwd=launch_dir, check=True)
