##  Usage: ./cancel_snakemake_jobs.sh [ SNAKEMAKE_LOG_FILE ]
## 
##  This script will find all Slurm IDs in a snakemake log file
##   and issue 'scancel' to cancel them


if [ $# -eq 0 ]
then
   snakeout_file="Reports/snakemake.log"
else
   snakeout_file=$1
fi

JOB_IDS=( $(grep "external jobid" $snakeout_file | sed "s/^.*jobid '\(.*\)'.$/\1/") )

echo “Found ${#JOB_IDS[@]} SLURM IDs… Cancelling them…”
for id in ${JOB_IDS[@]}
do
   #echo "scancel $id"
   scancel $id
done

echo “Done.”
