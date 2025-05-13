#!/usr/bin/env bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=1g
#SBATCH --time=1-00:00:00
#SBATCH --parsable
#SBATCH -J "CCBR_nxf"
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output "log/slurm_%j.log"
#SBATCH --error "log/slurm_%j.log"

module load nextflow

export SINGULARITY_CACHEDIR=/gpfs/gsfs10/users/CCBR_Pipeliner/Tools/ccbr_tools/tools-dev-sovacool/.singularity
if ! command -v spooker 2>&1 >/dev/null; then export PATH="$PATH:/data/CCBR_Pipeliner/Tools/ccbr_tools/v0.2/bin/"; fi

nextflow run main.nf -stub
