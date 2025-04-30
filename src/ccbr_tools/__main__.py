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
from .send_email import send_email_msg
from .templates import use_quarto_ext, get_quarto_extensions
from .software import install as install_software


all_scripts = "All installed tools:\n" + "\n".join(
    [f"  {cmd}" for cmd in get_project_scripts()]
)


@click.group(
    cls=CustomClickGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
    epilog=all_scripts,
)
@click.version_option(get_version(), "-v", "--version", is_flag=True)
def cli():
    """
    Utilities for CCBR Bioinformatics Software

    For more options, run:
    ccbr_tools [command] --help

    https://ccbr.github.io/Tools/
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


@click.command()
@click.argument(
    "to_address",
    type=str,
    default="${USER}@hpc.nih.gov",
    required=False,
)
@click.argument(
    "text",
    type=str,
    default=None,
    required=False,
)
@click.option(
    "--subject",
    "-s",
    type=str,
    default="test email from python",
    required=False,
    help="The subject line of the email",
)
@click.option(
    "--attach-html",
    "-a",
    type=click.Path(exists=True),
    default=None,
    required=False,
    help="The file path to the HTML attachment",
)
@click.option(
    "--from-addr",
    "-r",
    type=str,
    default="${USER}@hpc.nih.gov",
    required=False,
    help="The email address of the sender",
)
@click.option(
    "--debug",
    "-d",
    help="Return the Email Message object without sending the email",
    type=bool,
    default=False,
    is_flag=True,
)
def send_email(to_address, text, subject, attach_html, from_addr, debug):
    """
    Send an email (works on biowulf)

    \b
    Arguments:
        to_address    The email address of the recipient
        text          The plain text content of the email
    """
    send_email_msg(to_address, text, subject, attach_html, from_addr, debug)


@click.command(epilog=f"Available extensions: {', '.join(get_quarto_extensions())}")
@click.argument(
    "ext_name",
    type=str,
    required=True,
)
def quarto_add(ext_name):
    """
    Add a quarto extension

    \b
    Arguments:
        ext_name    The name of the extension in ccbr_tools

    \b
    Examples:
        ccbr_tools quarto-add fnl

    """
    use_quarto_ext(ext_name)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("tool_name")
@click.argument("version_tag")
@click.option(
    "--run",
    is_flag=True,
    default=False,
    help="Execute the install script; otherwise, just print it. It is a good idea to dry-run this script first to ensure the commands are correct, then run again with --run.",
)
@click.option(
    "--branch",
    "branch_tag",
    default=None,
    help="Branch or tag to install from GitHub. Use this option if the version is not a tag, e.g. for testing development versions.",
)
@click.option(
    "--type",
    "software_type",
    default=None,
    help="Type of software to install. Must be a class in `ccbr_tools.software`. If not specified, the type will be determined automatically (i.e. for CCBR software).",
)
@click.option(
    "--hpc",
    "hpc",
    default=None,
    help="HPC to install on. If not specified, the HPC will be detected automatically.",
)
def install(tool_name, version_tag, run, branch_tag, software_type, hpc):
    """
    Install a specific version of a CCBR software package, tool, or pipeline on a supported HPC.

    \b
    Args:
        tool_name (str): The name of the software package to install.
        version_tag (str): The version tag to install.
    """
    install_software(
        tool_name,
        version_tag,
        dryrun=not run,
        branch_tag=branch_tag,
        software_type=software_type,
        debug=hpc,
    )


cli.add_command(send_email)
cli.add_command(quarto_add)
cli.add_command(install)
cli.add_command(cite)
cli.add_command(version)


def main():
    cli()


cli(prog_name="ccbr_tools")

if __name__ == "__main__":
    main()
