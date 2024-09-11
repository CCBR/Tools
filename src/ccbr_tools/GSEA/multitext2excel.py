"""
multitext2excel.py
    Reads a list of files to import as separate tabs in Excel

Created on Mon Aug  6 14:59:13 2018

Susan Huse
NIAID Center for Biological Research
Frederick National Laboratory for Cancer Research
Leidos Biomedical

v 1.0 - initial code version.
v 1.1 - updated to include first splitter markowitzte@nih.gov
"""
__author__ = "Susan Huse"
__date__ = "August 6, 2018"
__version__ = "1.1"
__copyright__ = "No copyright protection, can be used freely"

# import csv
import sys
import os
import re
import datetime
import pandas as pd
import glob

# import scipy
# import numpy

import argparse
from argparse import RawTextHelpFormatter
from ncbr_huse import (
    run_cmd,
    run_os_cmd,
    un_gzip,
    send_update,
    err_out,
    fasta_count,
    fasta_list,
)


####################################
#
# Functions
#
####################################

#
# Set up the parameters for the USEARCH command and run it
#


####################################
#
# Main
#
####################################


def main():
    # Usage statement
    parseStr = 'Reads a list of files and imports them each into a separate tab in one Excel spreadsheet.\n\n\
    Usage:\n\
        multitext2excel.py -o outfile -d directory -p filepattern -k delimiter -s namesplitter\n\
    Example:\n\
        multitext2excel.py -o MyResults.xlsx -d analysis -p ".txt" -k "\t" -s "."\n'

    parser = argparse.ArgumentParser(
        description=parseStr, formatter_class=RawTextHelpFormatter
    )
    #    parser.add_argument('-i', '--infile', required=True, nargs='?', type=argparse.FileType('r'), default=None,
    #                        help='Input file containing important things')
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        nargs="?",
        type=argparse.FileType("w"),
        default=None,
        help="Output file for important results",
    )
    parser.add_argument(
        "-d",
        "--indir",
        required=False,
        type=str,
        action="store",
        default=".",
        help='Input directory containing data files to import [default="."]',
    )
    parser.add_argument(
        "-p",
        "--pattern",
        required=True,
        type=str,
        help="Pattern used to create list of input data files",
    )
    parser.add_argument(
        "-k",
        "--delimiter",
        required=False,
        type=str,
        default="\t",
        help='character delimiter that separates columns in each of the input data files [default="\t"]',
    )
    parser.add_argument(
        "-s",
        "--splitter",
        required=False,
        type=str,
        default=".",
        help='character to split input filenames to create output tab names. Cuts everything to the right [default="."]',
    )
    parser.add_argument(
        "-f",
        "--firstsplitter",
        required=False,
        type=str,
        default="",
        help='character to split input filenames to create output tab names. Cuts everything to the left [default=""]',
    )

    #
    # Set up the variables and the log file
    #
    args = parser.parse_args()
    #    infile = args.infile
    outfile = args.outfile
    pattern = args.pattern
    delimiter = args.delimiter
    splitter = args.splitter
    firstsplitter = args.firstsplitter
    indir = args.indir

    thedate = str(datetime.datetime.now()).split()[0]
    thedate = re.sub("-", "", thedate)

    # Set up the log file
    log = open("multitext2excel" + ".log", "a")
    log.write("\n" + str(datetime.datetime.now()) + "\n")
    log.write(" ".join(sys.argv) + "\n")
    log.write("multitext2excel.py version " + __version__ + "\n")
    log.flush()

    # Read for each matching file, read in and export to the output file
    pattern = "*" + pattern + "*"
    writer = pd.ExcelWriter(outfile.name)
    for filename in glob.glob(os.path.join(indir, pattern)):
        # Extract the output tab name
        # sheet_name = os.path.basename(filename).split(splitter)[0]
        sheet_name = re.sub(indir + "/", "", filename).split(splitter)[0]
        if firstsplitter != "":
            sheet_name = sheet_name.split(firstsplitter)[1]
        print(
            "Writing data from input file: {} to output tab: {}".format(
                filename, sheet_name
            )
        )

        # Read in the data
        df = pd.read_csv(filename, sep=delimiter, header=0, encoding="unicode_escape")

        # Write out the data
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    # Close it up!
    writer.save()

    #
    # Close out the log file
    #
    send_update(
        "multitext2excel.py successfully completed.  {} written.".format(outfile.name),
        log,
    )
    send_update(str(datetime.datetime.now()) + "\n", log)
    log.close()


if __name__ == "__main__":
    main()
