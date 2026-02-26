"""
CLI for pre-commit hooks
"""

import click
from ..pkg_util import (
    get_version,
    CustomClickGroup,
)
from .detect_absolute_paths import detect_absolute_paths


@click.group(
    cls=CustomClickGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
def cli():
    """
    Pre-commit hooks for CCBR Bioinformatics Software

    For more options, run:
    ccbr_hooks [command] --help

    https://ccbr.github.io/Tools/hooks
    """
    pass


cli.add_command(detect_absolute_paths)


def main():
    cli(prog_name="ccbr-hooks")


if __name__ == "__main__":
    main()
