"""
Miscellaneous utility functions for the package
"""

from cffconvert.cli.create_citation import create_citation
from cffconvert.cli.validate_or_write_output import validate_or_write_output
import click
import importlib.resources
import importlib.metadata
import pathlib
from time import localtime, strftime
import tomllib

from . import templates


class CustomClickGroup(click.Group):
    def format_epilog(self, ctx, formatter):
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)

    def list_commands(self, ctx: click.Context):
        """Preserve the order of subcommands when printing --help"""
        return list(self.commands)


def repo_base(*paths):
    """
    Get the absolute path to a file in the repository

    Args:
        *paths (str): Additional paths to join with the base path.

    Returns:
        path (str): The absolute path to the file in the repository.
    """
    basedir = pathlib.Path(__file__).absolute().parent
    return basedir.joinpath(*paths)


def get_version(repo_base=repo_base, debug=False):
    """
    Get the current version of the ccbr_tools package.

    Args:
        repo_base (function): A function that returns the base path of the repository.
        debug (bool): Print the path to the VERSION file (default: False).

    Returns:
        version (str): The version of the package.
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
        version (str): The version of the package.
    """
    importlib.metadata.metadata(pkg_name)["Version"]


def get_pyproject_toml(pkg_name="ccbr_tools", repo_base=repo_base):
    """
    Get the contents of the package's pyproject.toml file.

    Args:
        pkg_name (str): Name of the package (default: ccbr_tools).

    Returns:
        pyproject (dict): The contents of the pyproject.toml file.
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
        tools (list): A sorted list of CLI tool names.
    """
    return sorted(get_pyproject_toml(pkg_name=pkg_name)["project"]["scripts"].keys())


def get_external_scripts(pkg_name="ccbr_tools"):
    """
    Get list of standalone scripts included in the package

    Args:
        pkg_name (str): The name of the package. Defaults to "ccbr_tools".

    Returns:
        scripts (list): A list of standalone scripts included in the package.
    """
    return list(
        get_pyproject_toml(pkg_name=pkg_name)["tool"]["setuptools"]["script-files"]
    )


def print_citation(citation_file=repo_base("CITATION.cff"), output_format="bibtex"):
    """
    Prints the citation for the given citation file in the specified output format.

    Args:
        citation_file (str): The path to the citation file.
        output_format (str): The desired output format for the citation.
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


def read_template(template_name):
    """
    Read a template file

    Args:
        template_name (str): Name of the template file

    Returns:
        template (str): Contents of the template file
    """

    template_files = importlib.resources.files(templates)
    template_path = template_files / template_name
    with open(template_path, "rt") as template_file:
        return template_file.read()


def use_template(template_name, output_filepath=None, **kwargs):
    """
    Uses a template, formats variables, and write it to a file.
    Args:
        template_name (str): The name of the template to use.
        output_filepath (str, optional): The filepath to save the output file. If not provided, it will be written to `template_name` in the current working directory.
        **kwargs: Keyword arguments to fill in the template variables.
    Returns:
        None
    Raises:
        FileNotFoundError: If the template file is not found.
        IOError: If there is an error writing the output file.
    Examples:
        use_template("slurm_nxf_biowulf.sh", output_filepath="submit_slurm.sh", PIPELINE="CCBR_nxf", RUN_COMMAND="nextflow run main.nf -stub")
    """
    template_str = read_template(template_name)
    if not output_filepath:
        output_filepath = template_name
    with open(output_filepath, "wt") as outfile:
        outfile.write(template_str.format(**kwargs))
