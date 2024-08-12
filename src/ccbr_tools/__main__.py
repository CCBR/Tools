"""
Entry point for CCBR Tools
"""

import click
import cffconvert.cli.cli

from .util import get_version, OrderedCommands, print_citation, repo_base


@click.group(
    cls=OrderedCommands, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
def cli():
    """
    Utilities for CCBR Bioinformatics Software

    For more options, run:
    tool_name [command] --help"""
    pass


@click.command()
@click.argument(
    "citation_file",
    type=click.Path(exists=True),
    required=True,
    default=repo_base("CITATION.cff"),
)
@click.option(
    "--output-format",
    "-f",
    default="bibtex",
    help="Output format for the citation",
    type=cffconvert.cli.cli.options["outputformat"]["type"],
)
def cite(citation_file, output_format):
    """
    Print the citation in the desired format

    citation_file : Path to a file in Citation File Format (CFF) [default: the CFF for ccbr_tools]
    """
    print_citation(citation_file=citation_file, output_format=output_format)


cli.add_command(cite)


def main():
    cli()


cli(prog_name="ccbr_tools")

if __name__ == "__main__":
    main()
