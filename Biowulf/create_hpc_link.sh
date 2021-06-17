##  Usage: ./create_hpc_link.sh
## 
##  This script will print the HPC Datashare URL for accessing files in /data/CCBR/datashare
##   for all files in the current directory

ls $(pwd)/* | sed -e 's/\/data\/CCBR\/datashare/https:\/\/hpc.nih.gov\/~CCBR/'
