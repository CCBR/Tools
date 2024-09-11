"""
Reads a rnaseq pipeliner *_DEG_all_genes.txt file and outputs a prioritized list of Ensembl gene IDs for ToppFun

Author: Susan Huse

NIAID Center for Biological Research

Frederick National Laboratory for Cancer Research

Leidos Biomedical

- v 1.0 - initial code version.
- v 1.1 - updated for new column headers in pipeliner limma_DEG_all_genes.txt
- v 1.2 - top2Excel format is now csv rather than tab-delimited

"""

__author__ = "Susan Huse"
__date__ = "August 6, 2018"
__version__ = "1.1"
__copyright__ = "No copyright protection, can be used freely"

import sys
import os
import re
import datetime
import pandas as pd

import argparse
from argparse import RawTextHelpFormatter
from ncbr_huse import send_update


####################################
#
# Functions
#
####################################
def filter_by_p(x, nhits, pvalue, qvalue):
    # Filter the data to nhits, pvalue, qvalue
    x.sort_values(by=["p"], inplace=True)
    x = x[(x["p"] <= pvalue) & (x["q"] <= qvalue)]
    if x.shape[0] > nhits:
        x = x.head(nhits)
    return x


####################################
#
# Main
#
####################################


def main():
    # Usage statement
    parseStr = "Reads RNASeq differential expression output files\n\
and outputs a prioritized list of genes for use in GSEA or ToppFun.\n\
Will filter by both p and fdr values, and export up to nhits values.\n\
Reads several limma output versions (topTable, pipeliner, top2Excel).\n\
Outputs gene name and gsea rank for GSEA or Enssemble IDs for ToppFun.\n\
NB: GSEA cannot support hyphens in filenames, they will be replaced with underscores.\n\n\
Usage:\n\
    deg2gs.py -i infile -o outfile -n nHits -p pvalue -q fdrvalue -m method -s sheetname -f format\n\n\
Example:\n\
    deg2gs.py -i ExpAll_limma_DEG_all_genes.txt -o ExpAll_limma_all_genes.gsea.rnk -n 1000 -q 0.05 -m gsea -f pipeliner\n\
    deg2gs.py -i DEanalysis.xlsx -o DEanalysis.topp.rnk -n 1000 -p 1e-05 -q 5e-02 -m toppfun -f topTable -s Sheet1\n\n"

    parser = argparse.ArgumentParser(
        description=parseStr, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--infile",
        required=True,
        nargs="?",
        type=argparse.FileType("r"),
        default=None,
        help="Input file containing important things",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        action="store",
        type=str,
        default=None,
        help="Output file for important results",
    )
    parser.add_argument(
        "-m",
        "--method",
        type=str,
        action="store",
        default=None,
        choices=["gsea", "toppfun"],
        help="Method for gene set analysis (gsea or toppfun)",
    )
    parser.add_argument(
        "-n",
        "--nhits",
        type=int,
        action="store",
        required=False,
        default=500,
        help="Maximum number of top hits to extract, default = 500",
    )
    parser.add_argument(
        "-p",
        "--pvalue",
        type=float,
        action="store",
        required=False,
        default=0.05,
        help="Maximum p-value threshold to export, default = 0.05",
    )
    parser.add_argument(
        "-q",
        "--qvalue",
        type=float,
        action="store",
        required=False,
        default=0.10,
        help="Maximum FDR correction value to export, default = 0.10",
    )
    parser.add_argument(
        "-s",
        "--sheetname",
        type=str,
        action="store",
        default=None,
        help="Sheetname if input file is Excel rather than text (required for *.xlsx)",
    )
    parser.add_argument(
        "-f",
        "--fformat",
        type=str,
        action="store",
        default="pipeliner",
        choices=["pipeliner", "topTable", "top2Excel"],
        help="Input file format for running gsea."
        + "Pipeliner output has different column names than limma topTable",
    )

    #
    # Set up the variables and the log file
    #
    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile
    nhits = args.nhits
    pvalue = args.pvalue
    qvalue = args.qvalue
    method = args.method
    sheetname = args.sheetname
    fformat = args.fformat

    # don't really need a log file for this
    keepLog = False

    # replace hyphens with underscore, GSEA can't support hyphens
    # NB: this replaces for toppfun as well, so the names are consistent, but you don't have to do both
    fname = re.sub("-", "_", outfile)

    # Column names for each format, to read and write
    # NB: in_cols is not the same names as in the input file, but standardizes for this code
    # Assumes that ensid_gene is the row index
    if fformat == "pipeliner":
        in_cols = ["gene", "fc", "log2FC", "p", "q", "gsea"]

    elif fformat == "topTable":
        in_cols = ["log2FC", "AveExpr", "gsea", "p", "q", "B"]

    elif fformat == "top2Excel":
        in_cols = ["ensid", "gene", "log2FC", "AveExpr", "gsea", "p", "q", "B"]

    gsea_cols = ["gene", "gsea"]
    # top_cols = ['ensid']
    top_cols = ["gene"]

    # If keepLog then set it up
    if keepLog:
        thedate = str(datetime.datetime.now()).split()[0]
        thedate = re.sub("-", "", thedate)

        log = open("deg2gs" + ".log", "a")
        log.write("\n" + str(datetime.datetime.now()) + "\n")
        log.write(" ".join(sys.argv) + "\n")
        log.write("deg2gs.py version " + __version__ + "\n")
        log.write(
            "Exporting genes to {}, n={}, p={}, q={}, ".format(
                outfile.name, nhits, pvalue, qvalue
            )
        )
        log.flush()

    #
    # Import from Excel or tabSV, if Excel extension than excel otherwise csv
    #
    infile_name, infile_extension = os.path.splitext(infile.name)
    if infile_extension in [".xls", ".xlsx"]:
        if sheetname is None:
            err_out("Input Excel file requires sheet name", log)
        df = pd.read_excel(infile.name, sheet_name=sheetname, header=0, index_col=0)

    else:
        # df = pd.read_csv(infile, sep='\t', header=0, index_col=0)
        df = pd.read_csv(infile, sep=",", header=0, index_col=0)

    #
    # Set the columns based on the input format and the analysis method, but only if they match
    #
    if df.shape[1] != len(in_cols):
        errMsg = (
            '\nYour input file does not match the expected format "{}".\n'.format(
                fformat
            )
            + "Please check the file or the selected format and try again\n."
        )
        if keepLog:
            err_out(errMsg, log)
        else:
            print(errMsg)
            sys.exit(1)

    df.columns = in_cols

    # split the ensemblID|Gene if necessary
    if fformat == "topTable":  # and method == 'gsea':
        df["gene"] = [re.sub("^.*\|", "", i) for i in df.index.values.tolist()]

    # Filter the df to the p-values, FDR, and number of hits specified
    df = filter_by_p(df, nhits, pvalue, qvalue)

    #
    # Grab the relevant columns and write out the file
    #
    if method == "gsea":
        df = df.filter(items=gsea_cols)
        df.to_csv(fname, index=False, header=False, sep="\t")

    elif method == "toppfun":
        # # Get clean ensemble IDs for toppfun, strip off the .*$ from the Ensembl IDs and export them
        # # top2Excel already has it
        # if fformat != 'top2Excel':
        #     df['ensid'] = [re.sub("\..*$", "", i) for i in df.index.values.tolist()]
        df = df.filter(items=top_cols)
        df.to_csv(fname, index=False, header=False)

    #
    # Close out the log file
    #
    if keepLog:
        send_update("deg2gs.py successfully completed.  {} written.".format(fname), log)
        send_update(str(datetime.datetime.now()) + "\n", log)
        log.close()
    else:
        print("deg2gs.py successfully completed.  {} written.".format(fname))


if __name__ == "__main__":
    main()
