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
    """
    Get the absolute path to a file in the repository

    Args:
        path (str, optional): The path to the file. Defaults to __file__.
        *paths (str): Additional paths to join with the base path.

    Returns:
        str: The absolute path to the file in the repository.
    """
    basedir = pathlib.Path(path).absolute().parent
    return basedir.joinpath(*paths)


def get_version(debug=False, repo_base=repo_base):
    """
    Get the current version of the ccbr_tools package.

    Args:
        pkg_name (str): Name of the package (default: ccbr_tools).

    Returns:
        str: The version of the package.
    """
    version_path = repo_base("VERSION")
    if debug:
        print("VERSION file path:", version_path)
    with open(version_path, "r") as infile:
        return infile.read().strip().lstrip("v")


def get_package_version(pkg_name="ccbr_tools"):
    """
    Get the current version of a package from the metadata.

    Args:
        pkg_name (str): Name of the package (default: ccbr_tools).

    Returns:
        str: The version of the package.
    """
    importlib.metadata.metadata(pkg_name)["Version"]


def get_pyproject_toml(pkg_name="ccbr_tools", repo_base=repo_base):
    """
    Get the contents of the package's pyproject.toml file.

    Args:
        pkg_name (str): Name of the package (default: ccbr_tools).

    Returns:
        dict: The contents of the pyproject.toml file.
    """
    with open(repo_base("pyproject.toml"), "rb") as infile:
        toml_dict = tomllib.load(infile)
    return toml_dict


def get_project_scripts(pkg_name="ccbr_tools"):
    """
    Get a list of CLI tools in the package.

    Args:
        pkg_name (str): The name of the package. Defaults to "ccbr_tools".

    Returns:
        list: A sorted list of CLI tool names.
    """
    return sorted(get_pyproject_toml(pkg_name=pkg_name)["project"]["scripts"].keys())


def get_external_scripts(pkg_name="ccbr_tools"):
    """
    Get list of standalone scripts included in the package
    """
    list(get_pyproject_toml(pkg_name=pkg_name)["tool"]["setuptools"]["script-files"])


def print_citation(citation_file=repo_base("CITATION.cff"), output_format="bibtex"):
    """
    Prints the citation for the given citation file in the specified output format.

    Args:
        citation_file (str): The path to the citation file.
        output_format (str): The desired output format for the citation.

    Returns:
        None
    """
    citation = create_citation(citation_file, None)
    # click.echo(citation._implementation.cffobj['message'])
    validate_or_write_output(None, output_format, False, citation)


def msg(err_message):
    """
    Prints the error message with a timestamp.
    Args:
        err_message (str): The error message to be printed.
    Returns:
        None
    """
    tstamp = strftime("[%Y:%m:%d %H:%M:%S] ", localtime())
    click.echo(tstamp + err_message, err=True)


def msg_box(splash, errmsg=None):
    """
    Displays a message box with a given splash message.
    Args:
        splash (str): The splash message to be displayed.
        errmsg (str, optional): An error message to be displayed below the splash message. Defaults to None.
    """
    msg("-" * (len(splash) + 4))
    msg(f"| {splash} |")
    msg(("-" * (len(splash) + 4)))
    if errmsg:
        click.echo("\n" + errmsg, err=True)
