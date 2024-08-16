from ..pkg_util import repo_base, msg_box
from ..shell import shell_run
from .util import get_hpcname


def run_nextflow(
    nextfile_path=None,
    merge_config=None,
    threads=None,
    nextflow_args=None,
    mode="local",
    hpc_options={
        "biowulf": {"profile": "biowulf", "slurm": "assets/slurm_header_biowulf.sh"},
        "fnlcr": {
            "profile": "frce",
            "slurm": "assets/slurm_header_frce.sh",
        },
    },
):
    """Run a Nextflow workflow"""
    nextflow_command = ["nextflow", "run", nextfile_path]

    hpc = get_hpcname()
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
        profiles.add(hpc_options[hpc]["profile"])
    args_dict["-profile"] = ",".join(sorted(profiles))
    nextflow_command += list(f"{k} {v}" for k, v in args_dict.items())

    # Print nextflow command
    nextflow_command = " ".join(str(nf) for nf in nextflow_command)
    msg_box("Nextflow command", errmsg=nextflow_command)

    if mode == "slurm":
        slurm_filename = "submit_slurm.sh"
        with open(slurm_filename, "w") as sbatch_file:
            with open(repo_base(hpc_options[hpc]["slurm"]), "r") as template:
                sbatch_file.writelines(template.readlines())
            sbatch_file.write(nextflow_command)
        run_command = f"sbatch {slurm_filename}"
        msg_box("Slurm batch job", errmsg=run_command)
    elif mode == "local":
        if hpc:
            nextflow_command = f'bash -c "module load nextflow && {nextflow_command}"'
        run_command = nextflow_command
    else:
        raise ValueError(f"mode {mode} not recognized")
    shell_run(run_command, capture_output=False)
