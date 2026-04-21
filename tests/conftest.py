import pathlib

import pytest


@pytest.fixture
def data_dir():
    return pathlib.Path(__file__).resolve().parent / "data"


@pytest.fixture
def data_dir_rel():
    return pathlib.Path("tests") / "data"
