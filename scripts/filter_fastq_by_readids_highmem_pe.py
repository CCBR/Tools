#!/usr/bin/env python
import argparse
import os
import sys

import HTSeq


def get_sname(s):
    """Return the sample name from the input path."""
    sname = s.name
    sname = sname.split()[0]
    return sname


def fixoutfilename(f):
    """Return the normalized output filename."""
    outfqfilename = f
    dummy = outfqfilename.strip().split(".")
    if dummy[-1] == "gz":
        dummy.pop(-1)
        outfqfilename = ".".join(dummy)
    return outfqfilename


parser = argparse.ArgumentParser(description="Filter FASTQ by readids from PE reads")
parser.add_argument(
    "--infq", dest="infq", type=str, required=True, help="input FASTQ file"
)
parser.add_argument(
    "--infq2", dest="infq2", type=str, required=True, help="input FASTQ file"
)
parser.add_argument(
    "--outfq", dest="outfq", type=str, required=True, help="filtered output FASTQ file"
)
parser.add_argument(
    "--outfq2",
    dest="outfq2",
    type=str,
    required=True,
    help="filtered output FASTQ file",
)
parser.add_argument(
    "--readids",
    dest="readids",
    type=str,
    required=True,
    help="file with readids to keep (one readid per line)",
)
parser.add_argument(
    "--complement",
    dest="complement",
    action="store_true",
    help="complement the readid list, ie., include readids NOT in the list",
)
args = parser.parse_args()
with open(args.readids, "r") as _fh:
    rids = {x.strip() for x in _fh}
sequences = {get_sname(s): s for s in HTSeq.FastqReader(args.infq)}
sequences2 = {get_sname(s): s for s in HTSeq.FastqReader(args.infq2)}
if len(set(sequences.keys())) != len(
    set(sequences.keys()).intersection(set(sequences2.keys()))
):
    print("readids differ between input paired end mates")
    sys.exit()
if args.complement:
    rids = set(sequences.keys()) - rids
outfqfilename = fixoutfilename(args.outfq)
outfqfilename2 = fixoutfilename(args.outfq2)
with open(outfqfilename, "w") as outfqfile, open(outfqfilename2, "w") as outfqfile2:
    for rid in rids:
        s = sequences[rid]
        s.write_to_fastq_file(outfqfile)
        s = sequences2[rid]
        s.write_to_fastq_file(outfqfile2)
os.system("pigz -p4 -f " + outfqfilename)
os.system("pigz -p4 -f " + outfqfilename2)
