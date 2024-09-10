"""
Utility functions for shell command execution.

Example:
    >>> shell_run("echo Hello, World!")
    'Hello, World!\n'
    >>> shell_run("invalid_command")
    '/bin/sh: invalid_command: command not found\n'
"""

import contextlib
import io
import subprocess


def shell_run(command_str, capture_output=True, check=True, shell=True, text=True):
    """
    Run a shell command and return stdout/stderr

    Args:
        command_str (str): The shell command to be executed.
        capture_output (bool, optional): Whether to capture the command's output. Defaults to True.
        check (bool, optional): Whether to raise an exception if the command returns a non-zero exit status. Defaults to True.
        shell (bool, optional): Whether to run the command through the shell. Defaults to True.
        text (bool, optional): Whether to treat the command's input/output as text. Defaults to True.

    Returns:
        out (str): The combined stdout and stderr of the command, separated by a newline character.
    """
    out = subprocess.run(
        command_str, capture_output=capture_output, shell=shell, text=text, check=check
    )
    if capture_output:
        return concat_newline(out.stdout, out.stderr)


def exec_in_context(func: callable, *args: str, **kwargs: str):
    """
    Executes a function in a context manager and captures the output from stdout and stderr.

    Args:
        func (func): The function to be executed.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.

    Returns:
        str: The combined output from both stdout and stderr.
    """
    with (
        contextlib.redirect_stdout(io.StringIO()) as out_f,
        contextlib.redirect_stderr(io.StringIO()) as err_f,
    ):
        func(*args, **kwargs)
        out_combined = concat_newline(out_f.getvalue(), err_f.getvalue())
    return out_combined


def concat_newline(*args: str):
    """
    Concatenates strings with a newline character between non-empty arguments

    Args:
        *args: Variable length argument list of strings to be concatenated.

    Returns:
        str: The concatenated string with newline characters between each non-empty argument.
    """
    return "\n".join([arg for arg in args if arg])
