import pytest

import ccbr_tools.peek as peek
from ccbr_tools.shell import exec_in_context


def test_peek():
    out = exec_in_context(peek.peek, "tests/data/tab.tsv", 40)
    assert "tests/data/tab.tsv" in out
