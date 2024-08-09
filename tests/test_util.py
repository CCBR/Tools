from ccbr_tools.util import exec_in_context


def test_exec():
    assert exec_in_context(print, "hello", "world") == "hello world\n\n"
