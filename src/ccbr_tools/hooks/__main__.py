"""
CLI for pre-commit hooks
"""

import click
from ..pkg_util import (
    get_version,
    CustomClickGroup,
)
from .detect_absolute_paths import detect_absolute_paths
from .sync_nextflow_version import sync_nextflow_version


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
cli.add_command(sync_nextflow_version)


def main():
    """Run the CLI."""
    cli(prog_name="ccbr-hooks")


if __name__ == "__main__":
    main()
