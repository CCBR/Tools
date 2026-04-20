import ccbr_tools.peek as peek
from ccbr_tools.shell import exec_in_context


def test_peek(data_dir_rel):
    filepath = data_dir_rel / "tab.tsv"
    out = exec_in_context(peek.peek, str(filepath), 40)
    assert str(filepath) in out
