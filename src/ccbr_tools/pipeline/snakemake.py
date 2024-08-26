from ..pkg_util import repo_base, msg_box, use_template
from ..shell import shell_run
from .util import get_hpcname


def run(
    snakefile_path=None,
    snake_args=None,
    snake_default=None,
    threads=1,
    profile=None,
    configfile=None,
    cluster_config=None,
    mode="local",
    pipeline_name=None,
    debug=False,
    hpc_options={
        "biowulf": {"profile": "biowulf", "slurm": "slurm_smk_biowulf.sh"},
        "fnlcr": {
            "profile": "frce",
            "slurm": "slurm_smk_frce.sh",
        },
    },
):
    """
    Run a snakemake workflow

    Args:
        snakefile_path (str, optional): Path to the snakemake file. Defaults to None.
        configfile (str): Filepath of config file to pass with --configfile
        snake_args (list, optional): Additional snakemake arguments. Defaults to None.
        threads (int): Number of local threads to request
        snake_default (list): Snakemake args to pass to Snakemake
        profile (str): Name of Snakemake profile
        mode (str, optional): Execution mode. Defaults to "local".
        hpc_options (dict, optional): HPC options. Defaults to {"biowulf": {"profile": "biowulf", "slurm": "assets/slurm_header_biowulf.sh"}, "fnlcr": {"profile": "frce", "slurm": "assets/slurm_header_frce.sh"}}.

    Raises:
        ValueError: If mode is 'slurm' but no HPC environment was detected.

    Returns:
        None
    """
    snake_command = ["snakemake", "-s", snakefile_path]

    hpc = get_hpcname()
    if mode == "slurm" and not hpc:
        raise ValueError("mode is 'slurm' but no known HPC environment was detected")
    # add any additional snakemake commands
    args_dict = dict()
    # TODO set cluster config based on HPC if mode is slurm
    # TODO set config file to default if not provided
    # add threads
    if "--profile" not in snake_args and profile is None:
        snake_command += ["--cores", threads]

    # add snakemake default args
    # TODO --use-singularity
    if snake_default:
        snake_command += snake_default

    # add any additional snakemake commands
    if snake_args:
        snake_command += list(snake_args)

    # allow double-handling of --profile
    if profile:
        snake_command += ["--profile", profile]

    # Print snakemake command
    snakemake_command = " ".join(str(nf) for nf in snake_command)
    msg_box("Snakemake command", errmsg=snake_command)

    if mode == "slurm":
        slurm_filename = "submit_slurm.sh"
        use_template(
            hpc_options[hpc]["slurm"],
            output_filepath="submit_slurm.sh",
            PIPELINE=pipeline_name if pipeline_name else "CCBR_smk",
            RUN_COMMAND=snake_command,
        )
        with open(slurm_filename, "w") as sbatch_file:
            with open(repo_base(hpc_options[hpc]["slurm"]), "r") as template:
                sbatch_file.writelines(template.readlines())
            sbatch_file.write(snakemake_command)
        run_command = f"sbatch {slurm_filename}"
        msg_box("Slurm batch job", errmsg=run_command)
    elif mode == "local":
        if hpc:
            snakemake_command = (
                f'bash -c "module load {hpc.modules} && {snakemake_command}"'
            )
        run_command = snakemake_command
    else:
        raise ValueError(f"mode {mode} not recognized")

    # Run snakemake
    shell_run(run_command, capture_output=False)
