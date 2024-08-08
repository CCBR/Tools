#!/usr/local/bin/python
###################################################################
# Skyler Kuhn
# intersect
# Find the intersect of the two files
# Returns the inner join
# USAGE: intersect file1 file2
###################################################################
from __future__ import print_function
import sys


def indexFile(filename, joinindex, header):
    fh = open(filename, "r")
    filedict = {}
    if header == 1:
        firstline = next(fh).strip().replace('"', "").split("\t")
        filedict["headerstr"] = firstline

    for line in fh:
        linelist = line.strip().replace('"', "").split("\t")
        joinon = linelist[joinindex]
        filedict[joinon] = linelist

    fh.close()
    return filedict


def intersect(fileDict, file2, joinindex, header):
    fh2 = open(file2, "r")
    counter = 0

    if header == 1:
        firstline = next(fh2).strip().replace('"', "").split("\t")
        headerline = (
            "\t".join(fileDict["headerstr"]).rstrip("\n") + "\t" + "\t".join(firstline)
        )
        print(headerline)

    for line in fh2:
        linelist = line.strip().replace('"', "").split("\t")
        # print(linelist)
        joinon = linelist[joinindex]
        try:
            fileDict[joinon]
        except KeyError:
            continue  # joinon key is not in the file1, go to next line in file

        counter += 1
        intersection = (
            "\t".join(fileDict[joinon]).rstrip("\n") + "\t" + "\t".join(linelist)
        )
        print(intersection)

    # print(counter)
    fh2.close()


def main():
    # Join on column count starts at 0
    header = 0
    if "--header" in sys.argv:
        header = 1
    try:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        f1index = int(sys.argv[3])
        f2index = int(sys.argv[4])

    except IndexError:
        exit(
            "INCORRECT USGAE:\nintersect filename1 filename2 f1ColumnIndex F2ColumnIndex\n\t--Ex. intersect file1 file2 0 0"
        )

    indexedFile1 = indexFile(file1, f1index, header)
    intersect(indexedFile1, file2, f2index, header)


if __name__ == "__main__":
    main()
