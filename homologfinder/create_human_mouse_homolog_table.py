#!/usr/bin/env python3
import pandas as pd
cols = ["DB Class Key","Common Organism Name","Symbol"]
df = pd.read_csv("HOM_MouseHumanSequence.rpt", usecols=cols,sep="\t")
# human-mouse homologs file --> HOM_MouseHumanSequence.rpt
# can be downloaded from http://www.informatics.jax.org/faq/ORTH_dload.shtml
lookup = dict()
lookup2 = dict()
for index, row in df.iterrows():
	if not row["DB Class Key"] in lookup:
		lookup[row["DB Class Key"]] = dict()
		lookup[row["DB Class Key"]]["mouse, laboratory"] = list()
		lookup[row["DB Class Key"]]["human"] = list()
	if not row["Common Organism Name"] in lookup[row["DB Class Key"]]:
		continue
	lookup[row["DB Class Key"]][row["Common Organism Name"]].append(row["Symbol"])
for k,v in lookup.items():
	#print(",".join(v["mouse, laboratory"]),",".join(v["human"]),sep="\t")
	for l in v["mouse, laboratory"]:
		if not l in lookup2:
			lookup2[l] = list()
		lookup2[l].extend(v["human"])
	for l in v["human"]:
		if not l in lookup2:
			lookup2[l] = list()
		lookup2[l].extend(v["mouse, laboratory"])

for k,v in lookup2.items():
	print(k,",".join(v),sep="\t")
