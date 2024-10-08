#!/bin/bash
## AUTHOR ; Vishal N. Koparde, Ph.D., CCBR, NCI
## DATE : Feb 2021
## This scripts gathers cluster related statistics for jobs run on Biowulf using Snakemake by:
##   > extracting "external" jobids from snakemake.log files
##   > gather cluster stats for each job using "jobdata" and "jobhist" commands
##   > sorts output by job submission time
##   > output TSV file
##

function node2runpartition {
	node=$1
	node=$(echo $node|awk -F"," '{print $1}')
	partitions_requested=$2
	if [ "$partitions_requested" == "" ];then
	partitions_requested=$(sinfo|awk '{print $1}'|sort|uniq|grep -iv "partition"|sed "s/\*//g"|tr '\n' ' ')
	else
	partitions_requested=$(echo $partitions_requested|awk '{print $NF}'|tr "," " ")
	fi
	run_partition=$(for p in $partitions_requested;do if [ "$(freen -N $node|grep $p|awk '{print $1}'|grep $p|wc -l)" == "1" ]; then echo $p;break 1;fi;done)
	if [ "$run_partition" == "" ];then
		echo "unknown"
	else
		echo "$run_partition"
	fi
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
	jobdataarray["alloc_node_partition"]=$(node2runpartition ${jobdataarray["alloc_node"]} "")
	jobdataarray["run_node_partition"]=$(node2runpartition ${jobdataarray["node_list"]} ${jobdataarray["partition"]})
fi
jobdataarray["runtime"]=$(echo ${jobdataarray["queued"]} ${jobdataarray["elapsed"]}|awk '{print $1+$2}')

#change displaytimes
jobdataarray["runtime"]=$(displaytime ${jobdataarray["runtime"]})
jobdataarray["queued"]=$(displaytime ${jobdataarray["queued"]})
jobdataarray["elapsed"]=$(displaytime ${jobdataarray["elapsed"]})
jobdataarray["time_limit"]=$(displaytime ${jobdataarray["time_limit"]})

echo -ne "${jobdataarray["submit_time"]}\t"
echo -ne "${jobdataarray["human_submit_time"]}\t"
echo -ne "${jobdataarray["jobid"]};${jobdataarray["state"]};${jobdataarray["job_name"]}\t"
echo -ne "${jobdataarray["alloc_node"]};${jobdataarray["alloc_node_partition"]};${jobdataarray["node_list"]};${jobdataarray["run_node_partition"]}\t"
echo -ne "${jobdataarray["queued"]};${jobdataarray["elapsed"]};${jobdataarray["runtime"]};${jobdataarray["time_limit"]}\t"
echo -ne "${jobdataarray["avg_cpus"]};${jobdataarray["max_cpu_used"]};${jobdataarray["cpus_per_task"]}\t"
echo -ne "${jobdataarray["avg_mem"]};${jobdataarray["max_mem_used"]};${jobdataarray["total_mem"]}\t"
echo -ne "${jobdataarray["partition"]};${jobdataarray["qos"]}\t"
echo -ne "${jobdataarray["username"]};${jobdataarray["groupname"]};${jobdataarray["account"]}\t"
echo -ne "${jobdataarray["work_dir"]}\t"
echo -ne "${jobdataarray["std_out"]}\t"
echo -ne "${jobdataarray["std_err"]}\n"
}

if [ "$#" != "1" ];then
	echo " bash $0 <snakemake log file> "
	exit 1
fi

snakemakelogfile=$1
grep "with external jobid" $snakemakelogfile | awk '{print $NF}' | sed "s/['.]//g" | sort | uniq > ${snakemakelogfile}.jobids.lst
echo -ne "##SubmitTime\tHumanSubmitTime\tJobID;JobState;JobName\tAllocNode;AllocNodePartition;RunNode;RunNodePartition\tQueueTime;RunTime;Q+R;TimeLimit\tAvgCPU;MaxCPU;CPULimit\tAvgMEM;MaxMEM;MEMLimit\tPartition;QOS\tUsername;Group;Account\tWorkdir\tStdOut\tStdErr\n"
while read jid;do
	get_jobid_stats $jid
done < ${snakemakelogfile}.jobids.lst |sort -k1,1n
rm -f ${snakemakelogfile}.jobids.lst
