"""
Entry point for CCBR Tools
"""
import click

from .util import (
    get_version,
    OrderedCommands,
    print_citation,
)


@click.group(
    cls=OrderedCommands, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
@click.option(
    "--citation",
    is_flag=True,
    callback=print_citation,
    expose_value=False,
    is_eager=True,
    help="Print the citation in bibtex format and exit.",
)
def cli():
    """
    Utilities for CCBR Bioinformatics Software

    For more options, run:
    tool_name [command] --help"""
    pass


def main():
    cli()


cli(prog_name="ccbr_tools")

if __name__ == "__main__":
    main()
