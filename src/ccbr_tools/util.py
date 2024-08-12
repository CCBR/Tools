""" Miscellaneous utility functions """
import click
import os
from cffconvert.cli.create_citation import create_citation
from cffconvert.cli.validate_or_write_output import validate_or_write_output
from time import localtime, strftime


class OrderedCommands(click.Group):
    """Preserve the order of subcommands when printing --help"""

    def list_commands(self, ctx: click.Context):
        return list(self.commands)


def repo_base(*paths):
    """Get the absolute path to a file in the repository
    @return abs_path <str>
    """
    basedir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    return os.path.join(basedir, *paths)


def get_version(version_file=repo_base("VERSION")):
    """Get the current version
    @return version <str>
    """
    with open(version_file, "r") as vfile:
        version = f"v{vfile.read().strip()}"
    return version


def print_citation(
    context,
    param,
    value,
    citation_file=repo_base("CITATION.cff"),
    output_format="bibtex",
):
    if not value or context.resilient_parsing:
        return
    citation = create_citation(citation_file, None)
    # click.echo(citation._implementation.cffobj['message'])
    validate_or_write_output(None, output_format, False, citation)
    context.exit()


def msg(err_message):
    tstamp = strftime("[%Y:%m:%d %H:%M:%S] ", localtime())
    click.echo(tstamp + err_message, err=True)


def msg_box(splash, errmsg=None):
    msg("-" * (len(splash) + 4))
    msg(f"| {splash} |")
    msg(("-" * (len(splash) + 4)))
    if errmsg:
        click.echo("\n" + errmsg, err=True)
