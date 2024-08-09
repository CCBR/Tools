##  Usage: ./make_labels_for_pipeliner.sh
##
##  This script will look for *fastq.gz files in the current directory and
##   make a 'labels.txt' file for pipeliner when the FASTQs do not conform
##   to pipeliner's nomenclature (i.e. *_R1_001.fastq.gz instead of *.R1.fastq.gz)

ls -1 *.fastq.gz > oldnames.txt
## This sed command will remove the '_S###_' suffix and skip '_L001_' if there
ls *.fastq.gz | sed -re 's/_S[0-9]{1,3}_.*(R[1,2])_001/.\1/g' > newnames.txt
paste oldnames.txt newnames.txt > labels.txt
rm oldnames.txt newnames.txt
