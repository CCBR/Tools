#!/usr/bin/env bash
##  Usage: ./get_slurm_file_with_error.sh [ SNAKEMAKE_LOG_FILE ]
##
##  This script tries to find the first failed job and returns the slurm output file
##   that hopefully contains the error.  This was written for troubleshooting CCBR
##   Pipeliner, but should basically work for any Snakemake job on Biowulf you provide
##   as an argument

## Specifically, it does this:
## 1. Find the first occurrence of "Job failed" in the snakemake log file
## 2. Find the job id/rule name associated with it (usually occurs 3/4 lines before)
## 3. Find the Slurm ("external") ID of that job from when it was submitted
## 4. Find the slurm output file with that ID
##
## The analyst can then go through the slurm file to find/evaluate the error

## One liner version:
## grep -B 5 -m1 "Job failed" Reports/snakemake.log | grep "jobid: " | grep "job $(sed 's/^.*jobid: \(.*\)$/\1/')" Reports/snakemake.log |  slurm-$(sed "s/^.*jobid '\(.*\)'\.$/\1/").out

if [ $# -eq 0 ]
then
   SNAKEMAKE_LOG=Reports/snakemake.log
else
   SNAKEMAKE_LOG=$1
fi

jobid=$(grep -B 5 -m1 "Job failed" $SNAKEMAKE_LOG | grep "jobid: " | sed 's/^.*jobid: \(.*\)$/\1/')
rulename=$(grep -B 5 -m1 "Job failed" $SNAKEMAKE_LOG | grep "Error in rule " | sed 's/^.*Error in rule \(.*\):$/\1/')

if [ "$jobid" = "" ]
then
   echo ""
   echo "Couldn't find any explicit failures."
   echo ""
else

   slurmids=($(grep "job $jobid " $SNAKEMAKE_LOG | sed "s/^.*jobid '\(.*\)'\.$/\1/"))
   echo -e 'Rule Name\tSlurm ID(s)'
   echo -e $rulename'\t'$(IFS=, ; echo "${slurmids[*]}")
   echo ""

   if [ ${#slurmids[@]} -gt 0 ]; then
      echo "Slurm output files are listed below:"
      for slurmid in "${slurmids[@]}"; do
         #echo $slurmid
         errorfile="slurm-$slurmid.out"
         ## I'm not doing using find because that might take forever
         ##   when there's lots of files (like for large datasets)
         if [ ! -e $errorfile ]
         then
            errorfile=slurmfiles/$errorfile
            if [ ! -e $errorfile ]
            then
               echo "Hmm... can't find the slurm error file..."
            fi
         fi

         ls -lh $errorfile
      done
   fi
fi
