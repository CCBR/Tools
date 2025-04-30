import argparse
import pytest

from ccbr_tools.shell import exec_in_context
from ccbr_tools.jobby import (
    parse_time_to_seconds,
    parse_mem_to_gb,
    extract_jobids_from_file,
)


def test_parse_time_to_seconds():
    assert all(
        [
            parse_time_to_seconds(t) == expected
            for t, expected in [
                ("1-02:03:04", 93784),
                ("02:03:04", 7384),
                ("37:55.869", 2276),
                ("55.869", 56),
                ("", 0),
                (None, 0),
                ("invalid", 0),
            ]
        ]
    )


def test_parse_mem_to_gb():
    assert all(
        [
            parse_mem_to_gb(mem_str) == expected
            for mem_str, expected in [
                ("4000M", 3.90625),
                ("4G", 4.0),
                ("102400K", 0.09765625),
                ("1T", 1024.0),
                ("invalid", None),
                (None, None),
            ]
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


def test_extract_jobids_empty():
    assert extract_jobids_from_file("not_a_file") == []
