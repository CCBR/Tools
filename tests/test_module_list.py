import pytest

from ccbr_tools.shell import shell_run
from ccbr_tools.pipeline.hpc import parse_modules, list_modules, get_hpcname, is_loaded
from ccbr_tools.module_list import module_list


def test_module_list_cli():
    assert all(
        [
            shell_run("module_list") == "{}\n",
            shell_run("module_list not_a_module") == "not_loaded\n",
            "Show this help message" in shell_run("module_list -h"),
        ]
    )


def test_parse_modules():
    assert all(
        [
            parse_modules(
                "\nCurrently Loaded Modules:\n  1) ccbrpipeliner/7   3) singularity/4.2.2\n  2) java/17.0.3.1     4) nextflow/24.10.3\n\n \n\n"
            )
            == {
                "ccbrpipeliner": "7",
                "singularity": "4.2.2",
                "java": "17.0.3.1",
                "nextflow": "24.10.3",
            },
            parse_modules("1) module1 2) module2/1") == {"module1": "", "module2": "1"},
        ]
    )


def test_is_loaded():
    assert is_loaded("not_a_module") == False
