#!/bin/bash
ACCOUNT_SPONSOR=$(sacctmgr -rn list user | awk '{print $2}')
BUY_IN_NODE=$(scontrol show partitions | grep -i $ACCOUNT_SPONSOR -B1 | grep '^PartitionName' | cut -d '=' -f2 | grep -iv 'gpu'| tr '\n' ',' | sed 's/.$//')
echo $BUY_IN_NODE
