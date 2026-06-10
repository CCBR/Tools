import pathlib

import pytest


@pytest.fixture
def data_dir():
    """Return the absolute path to the test data directory."""
    return pathlib.Path(__file__).resolve().parent / "data"


@pytest.fixture
def data_dir_rel():
    """Return the relative path to the test data directory."""
    return pathlib.Path("tests") / "data"
