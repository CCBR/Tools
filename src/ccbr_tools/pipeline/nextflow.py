"""
Run Nextflow workflows in local and HPC environments.

Functions:
- run(nextfile_path=None, nextflow_args=None, mode="local", pipeline_name=None, debug=False, hpc_options={})
    Run a Nextflow workflow.
"""

from ..pkg_util import msg_box
from ..templates import use_template
from ..shell import shell_run
from .hpc import get_hpc
from .cache import get_singularity_cachedir


def run(
    nextfile_path,
    nextflow_args=[],
    mode="local",
    pipeline_name=None,
    debug=False,
    hpc=get_hpc(),
):
    """
    Run a Nextflow workflow

    Args:
        nextfile_path (str): Path to the Nextflow file.
        nextflow_args (list, optional): Additional Nextflow arguments. Defaults to an empty list.
        mode (str, optional): Execution mode. Defaults to "local".

    Raises:
        ValueError: If mode is 'slurm' but no HPC environment was detected.
    """
    if not pipeline_name:
        pipeline_name = "CCBR-nxf" if nextfile_path.endswith(".nf") else nextfile_path

    nextflow_command = ["nextflow", "run", nextfile_path]

    if mode == "slurm" and not hpc:
        raise ValueError("mode is 'slurm' but no HPC environment was detected")
    # add any additional Nextflow commands
    args_dict = dict()
    prev_arg = ""
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
    nextflow_command += list(f"{k} {v}" for k, v in args_dict.items())
    # turn command into a string
    nextflow_command = " ".join(str(nf) for nf in nextflow_command)

    if mode == "slurm":
        slurm_filename = "submit_slurm.sh"
        use_template(
            "submit_slurm.sh",
            PIPELINE=pipeline_name,
            MODULES=hpc.modules["nxf"],
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
            hpc_modules = hpc.modules["nxf"]
            nextflow_command = f'bash -c "module load {hpc_modules} && {hpc.env_vars} && {nextflow_command}"'
        run_command = nextflow_command
    else:
        raise ValueError(f"mode {mode} not recognized")

    # Run Nextflow
    msg_box("Nextflow command", errmsg=nextflow_command)
    if not debug:
        shell_run(run_command, capture_output=False)
