#!/usr/bin/env python3
"""
Display job information for past SLURM job IDs.

ABOUT:
    `jobby` is a command-line utility that collects and displays job metadata from SLURM-managed clusters.
    It supports retrieving job IDs from direct input, Snakemake logs, or Nextflow logs, and presents job
    status and resource usage in a standardized output format.

    Why?
    `jobby` aims to simplify and unify the job-querying process by abstracting away cluster-specific tools
    and normalizing output into common formats. `jobby` will ensure consistent reporting from multiple
    CCBR Snakemake and Nextflow pipelines when embedded in onsuccess/onerror/oncomplete blocks.

FEATURES:
    - Parses SLURM job IDs from CLI args, `.nextflow.log`, and `snakemake.log`.
    - Queries SLURM using `sacct` to gather job information such as state, runtime, CPU/memory usage, etc.
    - Converts time fields to seconds, memory fields to GB, and calculates CPU efficiency.
    - Supports multiple output formats: Markdown (default), TSV, JSON, and YAML.

USAGE:
    jobby <jobid1> [jobid2 ...] [--tsv|--json|--yaml]
    jobby <jobid1>,<jobid2> [--tsv|--json|--yaml]
    jobby snakemake.log [--tsv|--json|--yaml]
    jobby .nextflow.log [--tsv|--json|--yaml]

DEPENDENCIES:
    - Python 3.7+
    - pandas (required)
    - numpy (required)
    - PyYAML (optional, required only for --yaml output)

EXAMPLES:
    jobby 12345678 12345679
    jobby snakemake.log --json
    jobby .nextflow.log --yaml

"""

import subprocess
import sys
import os
import re
import warnings

# Graceful imports
try:
    import pandas as pd
except ImportError as err:
    raise Exception(
        "❌ Missing required package: pandas. Install it with `pip install pandas`."
    ) from err

try:
    import numpy as np
except ImportError as err:
    raise Exception(
        "❌ Missing required package: numpy. Install it with `pip install numpy`."
    ) from err

try:
    import yaml
except ImportError:
    yaml = None  # YAML is optional — we'll check later when needed

# Columns we can extract using sacct
COLUMNS = {
    "JobID": "JobId",
    "JobName": "JobName",
    "State": "JobState",
    "Elapsed": "RunTime",
    "AllocNodes": "NumNodes",
    "AllocCPUS": "NumCPUs",
    "TotalCPU": "TotalCPUTime",
    "ReqMem": "ReqMemGB",
    "MaxRSS": "MaxMemUsedGB",
    "ExitCode": "ExitCode",
    "Timelimit": "Timelimit",
    "NodeList": "NodeList",
    "Start": "StartTime",
    "End": "EndTime",
    "Submit": "QueuedTime",
    "WorkDir": "WorkDir",
}


def parse_time_to_seconds(t: str):
    """Convert SLURM time formats like '1-02:03:04', '02:03:04', '37:55.869', or '55.869' to seconds."""
    assert isinstance(t, str), "Input must be a string"
    total_seconds = np.nan
    try:
        if not t or t.strip() == "":
            pass
        else:
            if "-" in t:
                days, rest = t.split("-")
                days = int(days)
                t = rest
            else:
                days = 0

            parts = t.split(":")
            parts = [float(p) for p in parts]

            h = m = s = 0
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                m, s = parts
            elif len(parts) == 1:
                s = parts[0]

            total_seconds = int(
                round((int(days) * 86400 + int(h) * 3600 + int(m) * 60 + s))
            )
    except ValueError:
        warnings.warn(f"❌ Invalid time format: {t}. Time will be set to NaN.")
    return total_seconds


def parse_mem_to_gb(mem_str: str):
    """Convert SLURM memory strings like '4000M', '4G', '102400K' to GB as float."""
    assert isinstance(mem_str, str), "Input must be a string"
    result = np.nan
    try:
        if mem_str.endswith("K"):
            result = float(mem_str[:-1]) / (1024 * 1024)
        elif mem_str.endswith("M"):
            result = float(mem_str[:-1]) / 1024
        elif mem_str.endswith("G"):
            result = float(mem_str[:-1])
        elif mem_str.endswith("T"):
            result = float(mem_str[:-1]) * 1024
        else:
            result = float(mem_str) / (1024 * 1024)  # assume bytes
    except ValueError:
        warnings.warn(
            f"❌ Invalid memory format: {mem_str}. Memory will be set to NaN."
        )
    return result


def extract_jobids_from_file(filepath):
    """Extract SLURM job IDs from a Snakemake or Nextflow log file."""
    job_ids = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                # Match Snakemake pattern: external jobid '12345' or "12345"
                match_snakemake = re.search(r"external jobid\s+['\"](\d+)['\"]", line)
                if match_snakemake:
                    job_ids.append(match_snakemake.group(1))
                    continue  # no need to check further if matched

                # Match Nextflow pattern: (JOB ID: 12345)
                match_nextflow = re.search(
                    r"\[Task submitter\].*?>\s*jobId:\s*(\d+);", line
                )
                if match_nextflow:
                    job_ids.append(match_nextflow.group(1))
    except FileNotFoundError:
        warnings.warn(f"❌ File not found: {filepath}")
    return list(sorted(set(job_ids)))  # deduplicate


def get_sacct_info(job_ids):
    records = []
    for jobid in job_ids:
        try:
            sacct_cmd = [
                "sacct",
                "-j",
                str(jobid),
                f"--format={','.join(COLUMNS.keys())}",
                "-P",
                "--parsable2",
            ]
            output = subprocess.check_output(sacct_cmd, text=True).strip().split("\n")
            header = output[0].split("|")
            job_records = {}

            for line in output[1:]:
                parts = line.split("|")
                record_raw = dict(zip(header, parts))

                base_jobid = record_raw.get("JobID", "").split(".")[0]
                step_type = record_raw.get("JobID", "")

                if base_jobid not in job_records:
                    # First time seeing this JobID: store info
                    job_records[base_jobid] = record_raw
                else:
                    # If this is .batch, update resource usage fields
                    if step_type.endswith(".batch"):
                        for resource_field in ("MaxRSS", "AveRSS", "MaxVMSize"):
                            if (
                                resource_field in record_raw
                                and record_raw[resource_field]
                            ):
                                job_records[base_jobid][resource_field] = record_raw[
                                    resource_field
                                ]

            # Now, build the final records list
            for jobid, record_raw in job_records.items():
                record = {
                    new: record_raw.get(old, "N/A") for old, new in COLUMNS.items()
                }
                records.append(record)

        except subprocess.CalledProcessError:
            warnings.warn(f"❌ Failed to fetch info for JobID {jobid}")
    return records


def main():
    args = sys.argv[1:]

    if len(args) == 0 or "-h" in args or "--help" in args:
        print("Usage:")
        print("  jobby <jobid1> [jobid2 ...] [--tsv|--json|--yaml]")
        print("  jobby <jobid1>,<jobid2> [--tsv|--json|--yaml]")
        print("  jobby snakemake.log [--tsv|--json|--yaml]")
        print("  jobby .nextflow.log [--tsv|--json|--yaml]")
        sys.exit(1)

    output_format = "markdown"
    if "--tsv" in args:
        output_format = "tsv"
        args.remove("--tsv")
    elif "--json" in args:
        output_format = "json"
        args.remove("--json")
    elif "--yaml" in args:
        output_format = "yaml"
        args.remove("--yaml")
        if yaml is None:
            raise ImportError(
                "❌ YAML output requested but PyYAML is not installed. Install with `pip install pyyaml`."
            )

    # Case: 1 argument and it's a file
    if len(args) == 1 and os.path.isfile(args[0]):
        job_ids = extract_jobids_from_file(args[0])
    else:
        job_ids = args  # Treat all arguments as job IDs

    if not job_ids:
        raise ValueError("⚠️ No job IDs to process.")

    records = get_sacct_info(job_ids)
    if not records:
        raise ValueError("⚠️ No job data found.")

    df = pd.DataFrame(records)

    # convert Memory to GB
    df["ReqMemGB"] = df["ReqMemGB"].apply(parse_mem_to_gb).round(2)
    df["MaxMemUsedGB"] = df["MaxMemUsedGB"].apply(parse_mem_to_gb).round(2)

    # Split ExitCode into ExitCode and KillSignal
    exit_split = df["ExitCode"].str.split(":", expand=True)
    df["ExitCode"] = pd.to_numeric(exit_split[0], errors="coerce").astype("Int64")
    df["KillSignal"] = pd.to_numeric(exit_split[1], errors="coerce").astype("Int64")

    # Parse time columns to seconds
    df["ElapsedSec"] = df["RunTime"].apply(parse_time_to_seconds)
    df["CPUTimeSec"] = df["TotalCPUTime"].apply(parse_time_to_seconds)

    # Ensure AllocCPUs is numeric
    df["AllocCPUs"] = pd.to_numeric(df["NumCPUs"], errors="coerce")

    # Calculate CPU Efficiency
    df["CPUEfficiency"] = np.where(
        (df["ElapsedSec"] > 0) & (df["AllocCPUs"] > 0),
        df["CPUTimeSec"] / (df["ElapsedSec"] * df["AllocCPUs"]),
        np.nan,
    )

    # Optionally round CPUEfficiency to 2 decimals
    df["CPUEfficiency"] = (df["CPUEfficiency"] * 100).round(
        2
    )  # Expressed as a percentage

    # Reorder CPUEfficiency next to NumCPUs
    cols = list(df.columns)
    if "CPUEfficiency" in cols and "NumCPUs" in cols:
        # Move CPUEfficiency right after NumCPUs
        cols.insert(cols.index("NumCPUs") + 1, cols.pop(cols.index("CPUEfficiency")))
        df = df[cols]

    # Drop unwanted technical columns
    df = df.drop(
        columns=["TotalCPUTime", "AllocCPUs", "ElapsedSec", "CPUTimeSec"],
        errors="ignore",
    )

    # Reorder columns to keep KillSignal right after ExitCode
    cols = list(df.columns)
    if "KillSignal" in cols:
        # Move KillSignal to immediately after ExitCode
        cols.insert(cols.index("ExitCode") + 1, cols.pop(cols.index("KillSignal")))
        df = df[cols]

    # Output based on requested format
    if output_format == "markdown":
        print(df.to_markdown(index=False))
    elif output_format == "tsv":
        print(df.to_csv(sep="\t", index=False))
    elif output_format == "json":
        print(df.to_json(orient="records", indent=2))
    elif output_format == "yaml":
        print(yaml.dump(df.to_dict(orient="records"), sort_keys=False))
    else:
        raise ValueError(f"output format {output_format} not supported")


if __name__ == "__main__":
    main()
