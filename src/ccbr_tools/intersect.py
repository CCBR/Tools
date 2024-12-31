"""
Find the intersect of two files, returns the inner join

Original author: Skyler Kuhn (@skchronicles)

Usage:
    intersect file1 file2
"""

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


def run_intersect(args):
    usage_str = "USAGE:\nintersect filename1 filename2 f1ColumnIndex F2ColumnIndex\n\t--Ex. intersect file1 file2 0 0"
    # Join on column count starts at 0
    if "--help" in args or "-h" in args:
        print(usage_str)
    else:
        header = 0
        if "--header" in args:
            header = 1
        try:
            file1 = args[1]
            file2 = args[2]
            f1index = int(args[3])
            f2index = int(args[4])

        except IndexError:
            exit(
                "INCORRECT USAGE:\nintersect filename1 filename2 f1ColumnIndex F2ColumnIndex\n\t--Ex. intersect file1 file2 0 0"
            )

        indexedFile1 = indexFile(file1, f1index, header)
        intersect(indexedFile1, file2, f2index, header)


def main():
    run_intersect(sys.argv)


if __name__ == "__main__":
    main()
