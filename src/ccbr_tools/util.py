""" Miscellaneous utility functions """
import contextlib
import io
import subprocess


def shell_run(command_str):
    """Run a shell command and return stdout/stderr"""
    out = subprocess.run(command_str, capture_output=True, shell=True, text=True)
    return "\n".join([out.stdout, out.stderr])


def exec_in_context(func, *args, **kwargs):
    """Execute a function in a context manager to capture stdout/stderr"""
    with contextlib.redirect_stdout(io.StringIO()) as out_f, contextlib.redirect_stderr(
        io.StringIO()
    ) as err_f:
        func(*args, **kwargs)
        out_combined = "\n".join([out_f.getvalue(), err_f.getvalue()])
    return out_combined