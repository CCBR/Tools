""" Miscellaneous utility functions for the package """

from cffconvert.cli.create_citation import create_citation
from cffconvert.cli.validate_or_write_output import validate_or_write_output
import click
import importlib.resources
import importlib.metadata
import pathlib
from time import localtime, strftime
import tomllib


class CustomClickGroup(click.Group):
    def format_epilog(self, ctx, formatter):
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)

    def list_commands(self, ctx: click.Context):
        """Preserve the order of subcommands when printing --help"""
        return list(self.commands)


def repo_base(path=__file__, *paths):
    """Get the absolute path to a file in the repository
    @return abs_path <str>
    """
    basedir = pathlib.Path(path).absolute().parent
    return basedir.joinpath(*paths)


def get_version(debug=False, repo_base=repo_base):
    """Get the current version of the ccbr_tools package
    @param pkg_name <str> : name of the package (default: ccbr_tools)
    @return version <str>
    """
    version_path = repo_base("VERSION")
    if debug:
        print("VERSION file path:", version_path)
    with open(version_path, "r") as infile:
        return infile.read().strip().lstrip("v")


def get_package_version(pkg_name="ccbr_tools"):
    """Get the current version of a package from the metadata
    @param pkg_name <str> : name of the package (default: ccbr_tools)
    @return version <str>
    """
    importlib.metadata.metadata(pkg_name)["Version"]


def get_pyproject_toml(pkg_name="ccbr_tools", repo_base=repo_base):
    """Get the contents of the package's pyproject.toml file
    @param pkg_name <str> : name of the package (default: ccbr_tools)
    @return pyproject_toml <dict>
    """
    with open(repo_base("pyproject.toml"), "rb") as infile:
        toml_dict = tomllib.load(infile)
    return toml_dict


def get_project_scripts(pkg_name="ccbr_tools"):
    """
    Get list of CLI tools in the package
    """
    return sorted(get_pyproject_toml(pkg_name=pkg_name)["project"]["scripts"].keys())


def get_external_scripts(pkg_name="ccbr_tools"):
    """
    Get list of standalone scripts included in the package
    """
    list(get_pyproject_toml(pkg_name=pkg_name)["tool"]["setuptools"]["script-files"])


def print_citation(
    citation_file=repo_base("CITATION.cff"),
    output_format="bibtex",
):
    citation = create_citation(citation_file, None)
    # click.echo(citation._implementation.cffobj['message'])
    validate_or_write_output(None, output_format, False, citation)


def msg(err_message):
    tstamp = strftime("[%Y:%m:%d %H:%M:%S] ", localtime())
    click.echo(tstamp + err_message, err=True)


def msg_box(splash, errmsg=None):
    msg("-" * (len(splash) + 4))
    msg(f"| {splash} |")
    msg(("-" * (len(splash) + 4)))
    if errmsg:
        click.echo("\n" + errmsg, err=True)
