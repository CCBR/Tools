#!/bin/bash
## AUTHOR : Vishal N. Koparde, Ph.D., CCBR, NCI
## DATE : Mar 2021
## This scripts gathers cluster related statistics for jobs run on Biowulf using Snakemake by:
##   > extracting "external" jobids from snakemake.log files
##   > gather cluster stats for each job using sacct command
##   > sorts output by job submission time
##   > output TSV file
##

function node2runpartition {
	node=$1
	partitions_requested=$2
	run_partition=$(for p in `echo $partitions_requested|awk '{print $NF}'|tr "," " "`;do if [ "$(freen -N $node|grep $p|awk '{print $1}'|grep $p|wc -l)" == "1" ]; then echo $p;break 1;fi;done)
	if [ "$run_partition" == "" ];then
		echo "unknown"
	else
		echo "$run_partition"	
	fi
}


function get_jobid_stats {
jobid=$1
declare -A jobdataarray
notaccountablejob=$(jobhist $jid|grep "No accounting"|wc -l)
if [ "$notaccountablejob" == "1" ];then
	jobdataarray["submit_time"]="JOBNOTACCOUNTABLE"
	jobdataarray["jobid"]="$jobid"
else
	jobdata $jobid > ${jobid}.tmp
	awk -F"\t" '{if (NF==2) {print}}' ${jobid}.tmp > ${jobid}.data && rm -f ${jobid}.tmp
	while read a b;do
		jobdataarray["$a"]="$b"
	done < ${jobid}.data
	rm -f ${jobid}.data
	st=${jobdataarray["submit_time"]}
	jobdataarray["human_submit_time"]=$(date -d @$st|sed "s/ /_/g")
	jobdataarray["alloc_node_partition"]=$(node2runpartition ${jobdataarray["alloc_node"]} ${jobdataarray["partition"]})
	jobdataarray["run_node_partition"]=$(node2runpartition ${jobdataarray["node_list"]} ${jobdataarray["partition"]})
fi
echo -ne "${jobdataarray["submit_time"]}\t"
echo -ne "${jobdataarray["human_submit_time"]}\t"
echo -ne "${jobdataarray["jobid"]}:${jobdataarray["state"]}:${jobdataarray["job_name"]}\t"
echo -ne "${jobdataarray["alloc_node"]}:${jobdataarray["alloc_node_partition"]}:${jobdataarray["node_list"]}:${jobdataarray["run_node_partition"]}\t"
echo -ne "${jobdataarray["queued"]}:${jobdataarray["elapsed"]}:${jobdataarray["time_limit"]}\t"
echo -ne "${jobdataarray["avg_cpus"]}:${jobdataarray["max_cpu_used"]}:${jobdataarray["cpus_per_task"]}\t"
echo -ne "${jobdataarray["avg_mem"]}:${jobdataarray["max_mem_used"]}:${jobdataarray["total_mem"]}\t"
echo -ne "${jobdataarray["partition"]}:${jobdataarray["qos"]}\t"
echo -ne "${jobdataarray["username"]}:${jobdataarray["groupname"]}:${jobdataarray["account"]}\t"
echo -ne "${jobdataarray["work_dir"]}\t"
echo -ne "${jobdataarray["std_out"]}\t"
echo -ne "${jobdataarray["std_err"]}\n"
}

if [ "$#" != "1" ];then
	echo " bash $0 <snakemake log file> "
	exit 1
fi

# snakemakelogfile=$1
# grep "with external jobid" $snakemakelogfile | awk '{print $NF}' | sed "s/['.]//g" | sort | uniq > ${snakemakelogfile}.jobids.lst
# echo -ne "##SubmitTime\tHumanSubmitTime\tJobID:JobState:JobName\tAllocNode:AllocNodePartition:RunNode:RunNodePartition\tQueueTime:RunTime:TimeLimit\tAvgCPU:MaxCPU:CPULimit\tAvgMEM:MaxMEM:MEMLimit\tPartition:QOS\tUsername:Group:Account\tWorkdir\tStdOut\tStdErr\n"
# while read jid;do
# 	get_jobid_stats $jid
# done < ${snakemakelogfile}.jobids.lst |sort -k1,1n
# rm -f ${snakemakelogfile}.jobids.lst

function get_sacct_info {
	jobid=$1
	attribute=$2
	x=$(sacct -j $jobid --noheader --format="${attribute}%50"|head -n1|awk '{print $1}')
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
	jobdataarray["elaped"]=$(get_sacct_info $jobid "Elapsed")
	jobdataarray["time_limit"]=$(get_sacct_info $jobid "TimeLimit")


fi
echo -ne "${jobdataarray["submit_time"]}\t"
echo -ne "${jobdataarray["human_submit_time"]}\t"
echo -ne "${jobdataarray["jobid"]}:${jobdataarray["state"]}:${jobdataarray["job_name"]}\t"
echo -ne "${jobdataarray["node_list"]}:${jobdataarray["run_node_partition"]}\t"
echo -ne "${jobdataarray["queued"]}:${jobdataarray["elapsed"]}:${jobdataarray["time_limit"]}\t"
