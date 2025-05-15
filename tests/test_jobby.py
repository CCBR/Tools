import contextlib
import gzip
import io
import json
import os
import numpy as np
import pandas as pd
import pickle
import pytest

from ccbr_tools.jobby import (
    jobby,
    parse_time_to_seconds,
    parse_mem_to_gb,
    extract_jobids_from_file,
    get_sacct_info,
    records_to_df,
    format_df,
)
from ccbr_tools.pipeline.hpc import get_hpcname
from ccbr_tools.shell import shell_run

HPC = get_hpcname()


def generate_records():
    """
    Run this once on biowulf (must be run by sovacoolkl) to generate sacct info
    for downstream tests
    """
    records_smk = get_sacct_info(
        [
            "50456412",
            "50456444",
            "50456446",
            "50456448",
            "50456855",
            "50456856",
            "50456858",
            "50456859",
            "50456860",
            "50457081",
            "50457082",
            "50457083",
            "50457294",
            "50457690",
            "50457692",
            "50457694",
            "50457697",
            "50457699",
            "50457965",
            "50457966",
            "50457968",
            "50458236",
            "50459201",
            "50459203",
            "50459205",
            "50459393",
        ]
    )
    records_nxf = get_sacct_info(
        [
            "55256481",
            "55256959",
            "55256962",
            "55257214",
            "55257465",
            "55257468",
            "55257469",
            "55257648",
            "55257961",
        ]
    )
    with open("tests/data/jobby/records_smk.pkl", "wb") as f:
        pickle.dump(records_smk, f)
    with open("tests/data/jobby/records_nxf.pkl", "wb") as f:
        pickle.dump(records_nxf, f)


def generate_df():
    """
    Run this once to generate oracles for downstream tests
    """
    with open("tests/data/jobby/records_smk.pkl", "rb") as f:
        records_smk = pickle.load(f)
    with open("tests/data/jobby/records_nxf.pkl", "rb") as f:
        records_nxf = pickle.load(f)
    df_smk = records_to_df(records_smk)
    df_nxf = records_to_df(records_nxf)
    df_smk.to_pickle("tests/data/jobby/df_smk.pkl")
    df_nxf.to_pickle("tests/data/jobby/df_nxf.pkl")


def test_jobby_no_list():
    with pytest.raises(TypeError) as exc_info:
        jobby("50456412")
    assert "Expected a list of arguments" in str(exc_info.value)


@pytest.mark.skipif(HPC != "", reason="HPC is not empty")
def test_jobby_no_args():
    with pytest.warns(UserWarning) as exc_info:
        jobby([])
    assert "No job IDs to process" in str(exc_info[0].message)


@pytest.mark.skipif(HPC != "", reason="HPC is not empty")
def test_jobby_no_records():
    with pytest.raises(RuntimeError) as exc_info:
        jobby(["invalid_job_id"])
    assert "sacct command not found" in str(exc_info.value)


@pytest.mark.skipif(HPC != "biowulf", reason="only works on biowulf")
def test_jobby_no_records_biowulf():
    with pytest.warns(UserWarning) as exc_info:
        jobby(["invalid_job_id"])
    assert "Failed to fetch info for JobID" in str(exc_info[0].message)


@pytest.mark.skipif(
    HPC != "biowulf" and os.environ.get("USER") != "sovacoollkl",
    reason="only works for sovacoolkl on biowulf",
)
def test_jobby_biowulf():
    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        jobby(["--json", "50456412"])
    out_json = json.loads(stdout.getvalue())
    assert out_json == [
        {
            "JobId": "50456412",
            "JobName": "picard.name=KO_S4",
            "JobState": "COMPLETED",
            "RunTime": "00:00:39",
            "NumNodes": "1",
            "NumCPUs": "6",
            "CPUEfficiency": 17.09,
            "ReqMemGB": 110.0,
            "MaxMemUsedGB": 11.02,
            "ExitCode": 0,
            "KillSignal": 0,
            "Timelimit": "04:00:00",
            "NodeList": "cn1888",
            "StartTime": "2025-03-12T16:58:45",
            "EndTime": "2025-03-12T16:59:24",
            "QueuedTime": "2025-03-12T16:54:50",
            "WorkDir": "/gpfs/gsfs12/users/sovacoolkl/renee_test_hg38-45",
        }
    ]


def test_parse_time_to_seconds():
    results = [
        parse_time_to_seconds(t) == expected
        for t, expected in [
            ("1-02:03:04", 93784),
            ("02:03:04", 7384),
            ("37:55.869", 2276),
            ("55.869", 56),
        ]
    ]
    with pytest.warns(UserWarning):
        results.append(parse_time_to_seconds("invalid") is np.nan)
    assert all(results)


def test_parse_mem_to_gb():
    results = [
        parse_mem_to_gb(mem_str) == expected
        for mem_str, expected in [
            ("4000M", 3.90625),
            ("4G", 4.0),
            ("102400K", 0.09765625),
            ("1T", 1024.0),
        ]
    ]
    with pytest.warns(UserWarning):
        results.append(parse_mem_to_gb("invalid") is np.nan)
    assert all(results)


def test_assertions():
    with pytest.raises(AssertionError) as exc1:
        parse_time_to_seconds(False)
    with pytest.raises(AssertionError) as exc2:
        parse_mem_to_gb(0)
    assert all(
        [
            str(exc1.value) == "Input must be a string",
            str(exc2.value) == "Input must be a string",
        ]
    )


def test_extract_jobids_snakemake():
    assert extract_jobids_from_file("tests/data/jobby/snakemake.log") == [
        "50456412",
        "50456444",
        "50456446",
        "50456448",
        "50456855",
        "50456856",
        "50456858",
        "50456859",
        "50456860",
        "50457081",
        "50457082",
        "50457083",
        "50457294",
        "50457690",
        "50457692",
        "50457694",
        "50457697",
        "50457699",
        "50457965",
        "50457966",
        "50457968",
        "50458236",
        "50459201",
        "50459203",
        "50459205",
        "50459393",
    ]


def test_extract_jobids_nextflow():
    assert extract_jobids_from_file("tests/data/jobby/nextflow.log") == [
        "55256481",
        "55256959",
        "55256962",
        "55257214",
        "55257465",
        "55257468",
        "55257469",
        "55257648",
        "55257961",
    ]


@pytest.mark.filterwarnings("ignore:File not found")
def test_extract_jobids_empty():
    with pytest.warns(UserWarning):
        output = extract_jobids_from_file("not_a_file")
    assert output == []


def test_records_to_df_smk():
    with open("tests/data/jobby/records_smk.pkl", "rb") as f:
        records_smk = pickle.load(f)
    with open("tests/data/jobby/df_smk.pkl", "rb") as f:
        df_smk = pickle.load(f)
    pd.testing.assert_frame_equal(records_to_df(records_smk), df_smk)


def test_records_to_df_nxf():
    with open("tests/data/jobby/records_nxf.pkl", "rb") as f:
        records_nxf = pickle.load(f)
    with open("tests/data/jobby/df_nxf.pkl", "rb") as f:
        df_nxf = pickle.load(f)
    pd.testing.assert_frame_equal(records_to_df(records_nxf), df_nxf)


def test_format_df():
    with open("tests/data/jobby/df_nxf.pkl", "rb") as f:
        df_nxf = pickle.load(f)
    assertions = []
    for output_format in ["tsv", "json", "yaml"]:
        with gzip.open(f"tests/data/jobby/nextflow.log.{output_format}.gz", "rt") as f:
            expected = f.read()
        actual = (
            format_df(df_nxf, output_format) + "\n"
        )  # extra newline when files were printed
        assertions.append([actual, expected])
    assert all([actual == expected for actual, expected in assertions])


def test_jobby_version():
    output = shell_run("jobby --version")
    this_version = shell_run("ccbr_tools --version").split()[-1]
    assert all(
        [
            output.startswith("jobby: ccbr_tools version: "),
            output.strip().endswith(this_version),
        ]
    )
