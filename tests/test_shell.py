from ccbr_tools.shell import shell_run, exec_in_context, concat_newline


def test_exec():
    """Test exec."""
    assert exec_in_context(print, "hello", "world") == "hello world\n"


def test_shell_run():
    """Test shell run."""
    assert shell_run("echo hello world") == "hello world\n"


def test_concat_newline():
    """Test concat newline."""
    assert concat_newline("hello", "world") == "hello\nworld"
    assert concat_newline("goodbye", "") == "goodbye"
    assert concat_newline() == ""
