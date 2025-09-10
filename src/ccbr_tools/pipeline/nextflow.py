"""
Run Nextflow workflows in local and HPC environments.

Functions:
- init(output, pipeline_name='pipeline', **kwargs)
    Initialize the launch directory by copying the system default config files.
- run(nextfile_path=None, nextflow_args=None, mode="local", pipeline_name=None, debug=False, hpc_options={})
    Run a Nextflow workflow.
"""

import pathlib

from ..pkg_util import msg_box
from ..shell import shell_run
from ..templates import use_template
from .cache import get_singularity_cachedir
from .util import copy_config
from .hpc import get_hpc


def init(output, repo_base, pipeline_name="pipeline"):
    """Initialize the launch directory by copying the system default config files"""
    output_dir = output if isinstance(output, pathlib.Path) else pathlib.Path(output)
    msg_box(f"Initializing {pipeline_name} in {output_dir}")
    (output_dir / "log/").mkdir(parents=True, exist_ok=True)
    paths = ("nextflow.config", "conf/", "assets/")
    copy_config(paths, repo_base=repo_base, outdir=output_dir)


def run(
    nextfile_path,
    mode="local",
    force_all=False,
    pipeline_name=None,
    nextflow_args=None,
    debug=False,
    hpc=get_hpc(),
    hpc_modules="nextflow",
    hpc_walltime="1-00:00:00",
    hpc_memory="1G",
):
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

    Behavior:
        - Constructs the Nextflow command with appropriate arguments and profiles.
        - Adds or removes the '-resume' flag based on force_all.
        - For SLURM mode, generates a SLURM submission script and submits it via sbatch.
        - For local mode, optionally loads modules and environment variables before running Nextflow.
        - Shows a preview of the pipeline execution before running.
        - Executes the constructed command (unless debug is True).

    See also:
        - `~ccbr_tools.pipeline.hpc.get_hpc`: Retrieves the HPC environment object.
        - `~ccbr_tools.shell.shell_run`: Executes shell commands.
        - `~ccbr_tools.templates.use_template`: Generates files from templates.
    """
    if not pipeline_name:
        pipeline_name = "CCBR-nxf" if nextfile_path.endswith(".nf") else nextfile_path

    if mode == "slurm" and not hpc:
        raise ValueError("mode is 'slurm' but no HPC environment was detected")
    # add any additional Nextflow commands
    args_dict = dict()
    prev_arg = ""
    if nextflow_args:
        for arg in nextflow_args:
            if arg.startswith("-"):
                args_dict[arg] = ""
            elif prev_arg.startswith("-"):
                args_dict[prev_arg] = arg
            prev_arg = arg
    # make sure profile matches biowulf or frce
    profiles = (
        set(args_dict["-profile"].split(","))
        if "-profile" in args_dict.keys()
        else set()
    )
    if mode == "slurm":
        profiles.add("slurm")
    if hpc:
        profiles.add(hpc.name)
    if (
        profiles
    ):  # only add to the profiles if there are any. there are none when champagne is run on GitHub Actions.
        args_dict["-profile"] = ",".join(sorted(profiles))

    # use -resume by default, or do not use resume if force_all is True
    if force_all and "-resume" in args_dict.keys():
        args_dict.pop("-resume")
    elif not force_all and "-resume" not in args_dict.keys():
        args_dict["-resume"] = ""

    nextflow_command = " ".join(
        ["nextflow", "run", nextfile_path] + [f"{k} {v}" for k, v in args_dict.items()]
    )
    # Print a preview before launching the actual run
    if "-preview" not in args_dict.keys():
        preview_command = (
            (f'bash -c "module load {hpc_modules} && {nextflow_command} -preview"')
            if hpc and hpc_modules
            else nextflow_command + "-preview"
        )
        msg_box("Pipeline Preview", errmsg=preview_command)
        if not debug:
            shell_run(preview_command, shell=True, check=True, capture_output=False)

    if mode == "slurm":
        slurm_filename = "submit_slurm.sh"
        use_template(
            slurm_filename,
            output_filepath=slurm_filename,
            MEMORY=hpc_memory,
            WALLTIME=hpc_walltime,
            PIPELINE=pipeline_name,
            MODULES=hpc_modules,
            ENV_VARS="\n".join(
                (
                    hpc.env_vars,
                    # f"export SINGULARITY_CACHEDIR={get_singularity_cachedir()}",
                )
            ),  # TODO allow user override of singularity cache dir with CLI
            RUN_COMMAND=nextflow_command,
        )
        run_command = f"sbatch {slurm_filename}"
        msg_box("Slurm batch job", errmsg=run_command)
    elif mode == "local":
        if hpc:
            nextflow_command = f'bash -c "module load {hpc_modules} && {hpc.env_vars} && {nextflow_command}"'
        run_command = nextflow_command
    else:
        raise ValueError(f"mode {mode} not recognized")

    # Run Nextflow
    msg_box("Nextflow command", errmsg=nextflow_command)
    if not debug:
        shell_run(run_command, capture_output=False, check=False)
