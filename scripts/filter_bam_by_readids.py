#!/usr/bin/env python
import argparse

import pysam

parser = argparse.ArgumentParser(description="Filter BAM by readids")
parser.add_argument(
    "--inputBAM", dest="inputBAM", type=str, required=True, help="input BAM file"
)
parser.add_argument(
    "--outputBAM",
    dest="outputBAM",
    type=str,
    required=True,
    help="filtered output BAM file",
)
parser.add_argument(
    "--readids",
    dest="readids",
    type=str,
    required=True,
    help="file with readids to keep (one readid per line)",
)
args = parser.parse_args()
with open(args.readids, "r") as _fh:
    rids = [x.strip() for x in _fh]
inBAM = pysam.AlignmentFile(args.inputBAM, "rb")
outBAM = pysam.AlignmentFile(args.outputBAM, "wb", template=inBAM)
bigdict = {}

for count, read in enumerate(inBAM.fetch(), 1):
    if count % 1000000 == 0:
        print(f"{count} reads read!")
    qn = read.query_name
    if qn not in bigdict:
        bigdict[qn] = []
    bigdict[qn].append(read)
inBAM.close()

for r in rids:
    for read in bigdict[r]:
        outBAM.write(read)
outBAM.close()
