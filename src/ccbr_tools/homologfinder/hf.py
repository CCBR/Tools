#!/usr/bin/env python3

"""
About:
    hf or HomologFinder finds homologs in human and mouse.
    if the input gene or genelist is human, then it returns mouse homolog(s) and vice versa
USAGE:
    $ hf -h
Example:
    $ hf -g ZNF365
    $ hf -l Wdr53,Zfp365
    $ hf -f genelist.txt
"""

__version__ = "v1.0.0"
__author__ = "Vishal Koparde"
__email__ = "vishal.koparde@nih.gov"

import argparse
import io
import pandas as pd
import requests
import sys


def exit_w_msg(message):
    """Gracefully exit with proper message"""
    print("{} : EXITING!!".format(__file__))
    print(message)
    sys.exit()


def check_help(parser):
    """check if usage needs to be printed"""
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 1:
        print(__doc__)
        parser.print_help()
        parser.exit()
    return


def collect_args():
    """collect all the cli arguments"""
    # create parser
    parser = argparse.ArgumentParser(
        description="Get Human2Mouse (or Mouse2Human) homolog gene or genelist"
    )

    # add version
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s {}".format(__version__)
    )

    # add joblist
    parser.add_argument(
        "-g", "--gene", help="single gene name", required=False, type=str
    )

    # add snakemakelog
    parser.add_argument(
        "-l", "--genelist", help="comma separated gene list", required=False, type=str
    )

    # output file
    parser.add_argument(
        "-f",
        "--genelistfile",
        help="genelist in file (one gene per line)",
        type=str,
        required=False,
    )

    check_help(parser)

    # extract parsed arguments
    args = parser.parse_args()

    if (
        (args.gene and args.genelist)
        or (args.gene and args.genelistfile)
        or (args.genelist and args.genelistfile)
        or (args.gene and args.genelist and args.genelistfile)
    ):
        msg = "Only one can be provided -g or -l or -f"
        exit_w_msg(msg)

    return args


def process_genelist(gl, lookup):
    result = []
    for g in gl:
        if g in lookup:
            result.extend(lookup[g].split(","))
    return result


def process_args(args, lookup):
    if args.gene:
        r = process_genelist([args.gene], lookup)
    if args.genelist:
        gl = args.genelist
        r = process_genelist(gl.split(","), lookup)
    if args.genelistfile:
        with open(args.genelistfile) as f:
            lines = f.readlines()
        lines = list(map(lambda x: x.strip(), lines))
        r = process_genelist(lines, lookup)
    return r


def print_results(result):
    for g in result:
        print(g)


def read_lookup():
    lookup = dict()
    # read in lookup table from github
    url = "https://raw.githubusercontent.com/CCBR/Tools/master/homologfinder/human_mouse_homolog_lookup.txt"
    download = requests.get(url).content
    lookupdf = pd.read_csv(io.StringIO(download.decode("utf-8")), sep="\t")
    lookupdf.columns = ["geneName", "homologs"]
    for index, row in lookupdf.iterrows():
        lookup[row["geneName"]] = row["homologs"]
    return lookup


def create_homolog_table(rpt_file="HOM_MouseHumanSequence.rpt"):
    cols = ["DB Class Key", "Common Organism Name", "Symbol"]
    df = pd.read_csv(rpt_file, usecols=cols, sep="\t")
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
    for k, v in lookup.items():
        # print(",".join(v["mouse, laboratory"]),",".join(v["human"]),sep="\t")
        for l in v["mouse, laboratory"]:
            if not l in lookup2:
                lookup2[l] = list()
            lookup2[l].extend(v["human"])
        for l in v["human"]:
            if not l in lookup2:
                lookup2[l] = list()
            lookup2[l].extend(v["mouse, laboratory"])

    for k, v in lookup2.items():
        print(k, ",".join(v), sep="\t")


def main():
    # collect all arguments
    args = collect_args()
    # now that args are correct load in the lookup
    lookup = read_lookup()
    # process the arguments
    result = process_args(args, lookup)
    print_results(result)


if __name__ == "__main__":
    main()