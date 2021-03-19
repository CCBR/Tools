#!/bin/bash
## AUTHOR : Vishal N. Koparde, Ph.D., CCBR, NCI
## DATE : Mar 2021
## This scripts gathers cluster related statistics for jobs run on Biowulf using Snakemake by:
##   > extracting "external" jobids from snakemake.log files
##   > gather cluster stats for each job using sacct command
##   > sorts output by job submission time
##   > output TSV file
##


if [ "$#" != "1" ];then
	echo " bash $0 <snakemake log file> "
	exit 1
fi


function get_sacct_info {
	jobid=$1
	attribute=$2
	x=$(sacct -j $jobid --noheader --format="${attribute}%500"|head -n1|awk '{print $1}')
	echo $x
} 

function displaytime {
  local T=$1
  local D=$((T/60/60/24))
  local H=$((T/60/60%24))
  local M=$((T/60%60))
  local S=$((T%60))
  (( $D > 0 )) && printf '%d-' $D
  printf '%02d:%02d:%02d' $H $M $S
}

function print_jobid_stats {
jobid=$1
declare -A jobdataarray
nlines=$(sacct -j $jobid|wc -l)
	jobdataarray["jobid"]="$jobid"
if [ "$nlines" == "2" ];then
	jobdataarray["submit_time"]="JOBNOTACCOUNTABLE"
else
	export SLURM_TIME_FORMAT="%s" # epoch time
	jobdataarray["submit_time"]=$(get_sacct_info $jobid "Submit")
	jobdataarray["start"]=$(get_sacct_info $jobid "Start")
	jobdataarray["end"]=$(get_sacct_info $jobid "End")
	st=${jobdataarray["submit_time"]}
	jobdataarray["human_submit_time"]=$(date -d @$st|sed "s/ /_/g")
	jobdataarray["state"]=$(get_sacct_info $jobid "State")
	jobdataarray["job_name"]=$(get_sacct_info $jobid "JobName")
	jobdataarray["node_list"]=$(get_sacct_info $jobid "Nodelist")
	jobdataarray["run_node_partition"]=$(get_sacct_info $jobid "Partition")
	qt=$(echo ${jobdataarray["start"]} ${jobdataarray["submit_time"]}|awk '{print $1-$2}')
	jobdataarray["queued"]=$(displaytime $qt)
	jobdataarray["elapsed"]=$(get_sacct_info $jobid "Elapsed")
	jobdataarray["time_limit"]=$(get_sacct_info $jobid "TimeLimit")
	jobdataarray["reqcpus"]=$(get_sacct_info $jobid "ReqCPUS")
	jobdataarray["alloccpus"]=$(get_sacct_info $jobid "AllocCPUS")
	jobdataarray["req_mem"]=$(get_sacct_info $jobid "ReqMem")
	jobdataarray["qos"]=$(get_sacct_info $jobid "QOS")
	jobdataarray["username"]=$(get_sacct_info $jobid "user")
	jobdataarray["groupname"]=$(get_sacct_info $jobid "group")
	jobdataarray["account"]=$(get_sacct_info $jobid "account")
	jobdataarray["workdir"]=$(get_sacct_info $jobid "workdir")


fi
echo -ne "${jobdataarray["submit_time"]}\t"
echo -ne "${jobdataarray["human_submit_time"]}\t"
echo -ne "${jobdataarray["jobid"]};${jobdataarray["state"]};${jobdataarray["job_name"]}\t"
echo -ne "${jobdataarray["node_list"]};${jobdataarray["run_node_partition"]};${jobdataarray["qos"]}\t"
echo -ne "${jobdataarray["queued"]};${jobdataarray["elapsed"]};${jobdataarray["time_limit"]}\t"
echo -ne "${jobdataarray["reqcpus"]};${jobdataarray["alloccpus"]}\t"
echo -ne "${jobdataarray["req_mem"]}\t"
echo -ne "${jobdataarray["username"]};${jobdataarray["groupname"]};${jobdataarray["account"]}\t"
echo -ne "${jobdataarray["workdir"]}\n"
}


snakemakelogfile=$1
grep "with external jobid" $snakemakelogfile | awk '{print $NF}' | sed "s/['.]//g" | sort | uniq > ${snakemakelogfile}.jobids.lst
echo -ne "##SubmitTime\tHumanSubmitTime\tJobID:JobState:JobName\tNode;Partition:QOS\tQueueTime;RunTime;TimeLimit\tReqCPU;AllocCPU\tReqMEM\tUsername:Group:Account\tWorkdir\n"
while read jid;do
	print_jobid_stats $jid
done < ${snakemakelogfile}.jobids.lst |sort -k1,1n
rm -f ${snakemakelogfile}.jobids.lst
