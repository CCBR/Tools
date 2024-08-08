#!/usr/bin/env python3

"""
About:
    This wrapper script works only on BIOWULF!
    This script usage the "dashboard_cli" utility on biowulf to get HPC usage metadata
    for a list of slurm jobids. These slurm jobids can be either provided at command
    line or extracted from a snakemake.log file. Using snakemake.log file option together
    with --failonly option lists path to the STDERR files for failed jobs. This can be
    very useful to debug failed Snakemake workflows.
USAGE:
    $ jobinfo -h
Example:
    $ jobinfo -j 123456,7891011
    $ jobinfo -s /path/to/snakemake.log
    $ jobinfo -j 123456,7891011 -o /path/to/report.tsv
    $ jobinfo -s /path/to/snakemake.log --failonly
"""

__version__ = "v1.0.0"
__author__ = "Vishal Koparde"
__email__ = "vishal.koparde@nih.gov"

import argparse, subprocess, json, os, datetime, time, textwrap, sys
import pandas as pd

# SHORT_FIELDS used to display on screen
SHORT_FIELDS = "jobid,state,jobname,elapsed_time,timelimit,time_util,cpus,max_cpu_util,mem,max_mem_util,exit_code"
FAILONLY_FIELDS = "jobid,jobname,elapsed_time,timelimit,time_util,cpus,max_cpu_util,mem,max_mem_util,state_reason,eval,exit_code,std_err"
# LONG_FIELDS used to write to output file
LONG_FIELDS = "jobid,jobname,state,state_reason,eval,exit_code,nodelist,partition,qos,submit_time,queued_time,queued_time_seconds,elapsed_time,elapsed_time_seconds,timelimit,timelimit_seconds,user,cpus,cpu_min,cpu_avg,cpu_max,mem,mem_min,mem_avg,mem_max,gres,work_dir,std_out,std_err"
FAILONLY = "FAILED,TIMEOUT"

# change FAILONLY state .. for debugging only
# FAILONLY="TIMEOUT"


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


def check_host():
    if (
        os.environ.get("HOSTNAME") == "biowulf.nih.gov"
        or os.environ.get("HOSTNAME") == "helix.nih.gov"
    ):
        pass
    else:
        exit_w_msg("This script only works on BIOWULF!")


def collect_args():
    # create parser
    parser = argparse.ArgumentParser(
        description="Get slurm job information using slurm job id or snakemake.log file"
    )

    # add version
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s {}".format(__version__)
    )

    # add joblist
    parser.add_argument(
        "-j",
        "--joblist",
        help="comma separated list of jobids. Cannot be used together with -s option.",
        required=False,
        type=str,
    )

    # add snakemakelog
    parser.add_argument(
        "-s",
        "--snakemakelog",
        help="snakemake.log file. Slurm jobids are extracted from here. Cannot be used together with -j option.",
        required=False,
        type=argparse.FileType("r"),
    )

    # output file
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output file. All jobs (all states) and all columns are reported in output file.",
        type=str,
        required=False,
    )

    # output only failed jobs
    parser.add_argument(
        "-f",
        "--failonly",
        help="output FAILED jobs only (onscreen). Path to the STDERR files for failed jobs. All jobs are reported with -o option.",
        action="store_true",
        required=False,
    )

    check_help(parser)

    # extract parsed arguments
    args = parser.parse_args()

    if args.output:
        args.output = os.path.abspath(args.output)
        if not os.access(os.path.dirname(args.output), os.W_OK):
            msg = "File is not writable: {}".format(args.output)
            exit_w_msg(msg)

    if args.joblist and args.snakemakelog:
        exit_w_msg("Either -j or -s (not BOTH) is required!")

    if args.joblist:
        jobids = args.joblist
        args.joblist = jobids.split(",")

    if (
        args.snakemakelog
    ):  # if snakemakelog file is given then extract the jobids from it.
        cmd = (
            'grep "external jobid" '
            + args.snakemakelog.name
            + ' | awk \'{print $NF}\' | sed "s/\'//g" | sed "s/\.//g"'
        )
        p1 = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        args.joblist = p1.stdout.strip().split("\n")

    return args


def mem2gb(memstr):
    if memstr == "0":
        return float("0")
    value, unit = memstr.split()
    if unit == "GB":
        return float(value)
    elif unit == "MB":
        return float(value) / 1024
    elif unit == "KB":
        return float(value) / 1024 / 1024


def check_int_set_zero(s):
    if s == "":
        s = 0
    else:
        s = int(s)
    return s


def time2sec(timestr):
    debug = 0
    dayHMSstr_list = timestr.split("-")
    if debug == 1:
        print(timestr)
    if debug == 1:
        print(dayHMSstr_list)
    if debug == 1:
        print(len(dayHMSstr_list))
    if len(dayHMSstr_list) == 2:
        day = check_int_set_zero(dayHMSstr_list[0])
        HMSstr = dayHMSstr_list[1]
    else:
        day = 0
        HMSstr = dayHMSstr_list[0]
    HMSstr_list = HMSstr.split(":")
    if debug == 1:
        print(HMSstr)
    if debug == 1:
        print(HMSstr_list)
    if len(HMSstr_list) == 3:
        hour = check_int_set_zero(HMSstr_list[0])
        minutes = check_int_set_zero(HMSstr_list[1])
        sec = check_int_set_zero(HMSstr_list[2])
    elif len(HMSstr_list) == 2:
        hour = 0
        minutes = check_int_set_zero(HMSstr_list[0])
        sec = check_int_set_zero(HMSstr_list[1])
    elif len(HMSstr_list) == 1:
        hour = 0
        minutes = 0
        sec = check_int_set_zero(HMSstr_list[0])
    if debug == 1:
        print(day, hour, minutes, sec)
    sec += int(day) * 24 * 60 * 60
    if debug == 1:
        print(day, hour, minutes, sec)
    sec += int(hour) * 60 * 60
    if debug == 1:
        print(day, hour, minutes, sec)
    sec += int(minutes) * 60
    if debug == 1:
        print(day, hour, minutes, sec)
    return float(sec)


def get_jobinfo(args):
    # cmd = '/usr/local/bin/dashboard_cli jobs --joblist ' + ",".join(args.joblist[0:10]) + " --archive --json --fields " + LONG_FIELDS
    cmd = (
        "/usr/local/bin/dashboard_cli jobs --joblist "
        + ",".join(args.joblist)
        + " --archive --json --fields "
        + LONG_FIELDS
    )
    p1 = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if p1.returncode != 0:
        exit_w_msg("dashboard_cli failed!")
    p1_json = json.loads(p1.stdout)
    p1_table = pd.json_normalize(p1_json)
    p1_table["epochtime"] = p1_table.apply(
        lambda row: time.mktime(
            datetime.datetime.strptime(row.submit_time, "%Y-%m-%dT%H:%M:%S").timetuple()
        ),
        axis=1,
    )
    p1_table = p1_table.sort_values(by=["epochtime"])
    p1_table["max_cpu_util"] = p1_table.apply(
        lambda row: "-"
        if row["cpu_max"] == "-"
        else "%.2f" % (float(row["cpu_max"]) * 100 / int(row["cpus"])) + " %",
        axis=1,
    )
    p1_table["max_mem_util"] = p1_table.apply(
        lambda row: "-"
        if row["mem_max"] == "-"
        else "%.2f" % (mem2gb(row["mem_max"]) * 100 / mem2gb(row["mem"])) + " %",
        axis=1,
    )
    p1_table["queued_time_seconds"] = p1_table.apply(
        lambda row: "%d" % (int(time2sec(row["queued_time"]))), axis=1
    )
    p1_table["elapsed_time_seconds"] = p1_table.apply(
        lambda row: "%d" % (int(time2sec(row["elapsed_time"]))), axis=1
    )
    p1_table["timelimit_seconds"] = p1_table.apply(
        lambda row: "%d" % (int(time2sec(row["timelimit"]))), axis=1
    )
    p1_table["time_util"] = p1_table.apply(
        lambda row: "%.2f"
        % (float(row["elapsed_time_seconds"]) * 100 / float(row["timelimit_seconds"]))
        + " %"
        if float(row["timelimit_seconds"]) != 0
        else "- %",
        axis=1,
    )
    if args.output:
        try:
            if not p1_table.empty:
                p1_table.to_csv(
                    args.output,
                    sep="\t",
                    header=True,
                    index=False,
                    columns=LONG_FIELDS.split(","),
                )
        except:
            msg = "File is not writable: {}".format(args.output)
            exit_w_msg(msg)
    return p1_table


def filter_rows(func):
    def wrapper(t, args):
        if args.failonly:
            t = t[t["state"].isin(FAILONLY.split(","))]
        func(t, args)

    return wrapper


@filter_rows
def print2screen(t, args):
    onscreenfields = SHORT_FIELDS
    if args.failonly:
        onscreenfields = FAILONLY_FIELDS
    if t.empty:
        print("Good News!! You have ZERO FAILED jobs!")
    else:
        print(
            t.to_string(index=False, justify="left", columns=onscreenfields.split(","))
        )


def main():
    # check host
    check_host()
    # collect all arguments
    args = collect_args()
    # query dashboard_cli to get details as a pandas table
    t = get_jobinfo(args)
    # filter table, print to screen and write to output file
    print2screen(t, args)


if __name__ == "__main__":
    main()
