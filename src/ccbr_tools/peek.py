"""
Take a peek at tab-delimited files

Usage:
    peek <file.tsv> [buffer]
"""

from __future__ import print_function
from pathlib import Path
import sys


def usage():
    """Print usage information and exit program"""
    bin_stem = Path(sys.argv[0]).stem
    print(f"USAGE: {bin_stem} <file.tsv> [buffer]\n")
    print("Assumptions:\n\tInput file is tab delimited")
    print("\t └── Globbing supported: *.txt\n")
    print("Optional:\n\tbuffer = 40 (default)")
    print("\t └── Changing buffer will increase/decrease output justification")
    sys.exit()


def pargs():
    """Basic command-line parser"""
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 1:
        usage()
    try:
        fname = sys.argv[1]
    except IndexError:
        usage()
    return


def max_string(data):
    """Given a list of strings, finds the maximum strign length"""
    max = -1
    for value in data:
        if len(value) > max:
            max = len(value)
    return max


def print_header(filename, length):
    """Print filenames and divider"""
    print("# {}".format(filename))
    print("{}".format("=" * length))


def justify(h, d, n, nr):
    """Calculates the spacing for justifying to the right"""
    xspaces = n - (h + d)
    if nr < 10:
        xspaces = xspaces - 2
    else:
        xspaces = xspaces - 3
    spacing = xspaces * " "
    return spacing


def pprint(headlist, data, linelength, fn):
    """Re-formats first two lines on file so columns are left justified and values are right justified"""
    # Print Filename
    print_header(fn, linelength)

    # Print NR and justified contents of 1st and 2nd line
    for i in range(len(headlist)):
        rownumber = i + 1

        # Attribute name and corresponding value
        column = headlist[i].lstrip().rstrip()
        if not column:
            column = "NULL"
        value = data[i].lstrip().rstrip()

        # Calculate spacing for justifying to the right
        insert_spaces = justify(len(column), len(value), linelength, rownumber)
        print("{} {}{}{}".format(rownumber, column, insert_spaces, value))


def peek(filename, buffer, delim="\t"):
    pargs()

    # Getting contents of first line
    try:
        fh = open(filename, "r")
    except IOError as e:
        # File does not exist
        print("\n{}\nPlease check you filename!\n\n".format(e))
        usage()

    headerlist = fh.readline().split(delim)
    fh.close()

    # Getting contents of second line
    fh = open(filename, "r")
    try:
        datalist = fh.readlines()[1].split(delim)
    except IndexError:
        datalist = ["EMPTY_FIELD"]
    fh.close()

    max_attr_length = max_string(datalist)
    total_length = max_attr_length + buffer

    # Pretty print data (Right justify results)
    pprint(headerlist, datalist, total_length, filename)
    print()


def main():
    # Checking command-line usage before parsing
    pargs()

    try:
        buffer = int(sys.argv[-1])
        sys.argv.pop(-1)
    except IndexError:
        buffer = 40
    except ValueError:
        buffer = 40

    # Paring file(s) contents to support globbing
    for file in sys.argv[1:]:
        peek(file, buffer)


if __name__ == "__main__":
    main()
