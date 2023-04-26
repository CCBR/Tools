#!/bin/bash
# trying to find out which VPN you are connected to??

if [[ "$HOSTNAME" == "biowulf.nih.gov" ]]
then
	echo "DO NOT RUN THIS ON BIOWULF HEADNODE! This is script is meant for your laptop."
	exit 1
elif [[ "$HOSTNAME" == "helix.nih.gov" ]]
then
	echo "DO NOT RUN THIS ON HELIX! This script is meant for your laptop."
	exit 1
elif [[ "$HOSTNAME =~ cn[0-9]{4}$ ]]
then
	echo "DO NOT RUN THIS ON a BIOWULF interactive node! This script is meant for your laptop"
	exit 1
fi

# get ip
ip=$(ifconfig -a|grep "inet 10."|awk '{print $2}')

if [[ "$ip" == "" ]]
then
	echo "Are you really connected to VPN?? Doesnt look like it!"
	exit 1
fi

echo "Your VPN IP is $ip"

numbertwo=$(echo $ip|awk -F"." '{print $2}')

if [[ "$numbertwo" == "247" || "$numbertwo" == "248" ]]
then
	echo "You are connected to the FREDERICK VPN!"
	exit 0
elif [[ "$numbertwo" == "242" || "$numbertwo" == "243" ]]
then
	echo "You are connected to the BETHESDA VPN!"
	exit 0
else 
	echo "Sorry, I cannot guess which VPN you are connect to!"
	exit 0
fi
