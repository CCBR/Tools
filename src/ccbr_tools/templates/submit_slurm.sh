#!/usr/bin/env bash
#SBATCH --cpus-per-task=1
#SBATCH --mem={MEMORY}
#SBATCH --time={WALLTIME}
#SBATCH --parsable
#SBATCH -J "{PIPELINE}"
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output "log/slurm_%j.log"
#SBATCH --error "log/slurm_%j.log"

set -euo pipefail
modules=({MODULES})
if (( ${{#modules[@]}} )); then
    module load "${{modules[@]}}"
fi
{ENV_VARS}

{RUN_COMMAND}
