import HTSeq
import sys
import argparse
import os
def get_sname(s):
	sname=s.name
	sname=sname.split()[0]
	return sname

def fixoutfilename(f):
	outfqfilename=f
	dummy=outfqfilename.strip().split(".")
	if dummy[-1]=="gz":
		dummy.pop(-1)
		outfqfilename=".".join(dummy)	
	return outfqfilename


parser = argparse.ArgumentParser(description='Filter FASTQ by readids from PE reads')
parser.add_argument('--infq', dest='infq', type=str, required=True,
                    help='input FASTQ file')
parser.add_argument('--infq2', dest='infq2', type=str, required=True,
                    help='input FASTQ file')
parser.add_argument('--outfq', dest='outfq', type=str, required=True,
                    help='filtered output FASTQ file')
parser.add_argument('--outfq2', dest='outfq2', type=str, required=True,
                    help='filtered output FASTQ file')
parser.add_argument('--readids', dest='readids', type=str, required=True,
                    help='file with readids to keep (one readid per line)')
parser.add_argument('--complement', dest='complement', action='store_true', 
                    help='complement the readid list, ie., include readids NOT in the list')
args = parser.parse_args()
rids=set(map(lambda x:x.strip(),open(args.readids,'r').readlines()))
sequences = dict( (get_sname(s), s) for s in HTSeq.FastqReader(args.infq))
sequences2 = dict( (get_sname(s), s) for s in HTSeq.FastqReader(args.infq2))
if len(set(sequences.keys())) != len(set(sequences.keys()).intersection(set(sequences2.keys()))):
	print("readids differ between input paired end mates")
	exit()
if args.complement:
	rids=set(sequences.keys())-rids
outfqfilename=fixoutfilename(args.outfq)
outfqfile = open(outfqfilename,'w')
outfqfilename2=fixoutfilename(args.outfq2)
outfqfile2 = open(outfqfilename2,'w')
for rid in rids:
	s=sequences[rid]
	s.write_to_fastq_file(outfqfile)
	s=sequences2[rid]
	s.write_to_fastq_file(outfqfile2)
outfqfile.close()
outfqfile2.close()
os.system("pigz -p4 -f "+outfqfilename)
os.system("pigz -p4 -f "+outfqfilename2)
