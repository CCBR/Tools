"""
Entry point for CCBR Tools
"""

import click
import cffconvert.cli.cli

from .pkg_util import (
    get_project_scripts,
    get_version,
    print_citation,
    repo_base,
    CustomClickGroup,
)


all_commands = "All installed tools:\n" + "\n".join(
    [f"  {cmd}" for cmd in get_project_scripts()]
)


@click.group(
    cls=CustomClickGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
    epilog=all_commands,
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
def cli():
    """
    Utilities for CCBR Bioinformatics Software

    For more options, run:
    tool_name [command] --help

    """
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


@click.command()
@click.option(
    "--debug",
    "-d",
    help="Print the path to the VERSION file",
    type=bool,
    default=False,
    is_flag=True,
)
def version(debug):
    """
    Print the version of ccbr_tools
    """
    print(get_version(debug=debug))


cli.add_command(cite)
cli.add_command(version)


def main():
    cli()


cli(prog_name="ccbr_tools")

if __name__ == "__main__":
    main()
