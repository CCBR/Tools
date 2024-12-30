"""
Template files for CCBR Tools.

Templates:
    - `~ccbr_tools.templates.submit_slurm.sh`

Quarto extensions
    - `~ccbr_tools.templates._extensions.fnl`
"""

import importlib.resources
import pathlib
import shutil


def read_template(template_name):
    """
    Read a template file

    Args:
        template_name (str): Name of the template file

    Returns:
        template (str): Contents of the template file
    """

    template_files = importlib.resources.files(__package__)
    template_path = template_files / template_name
    with open(template_path, "rt") as template_file:
        return template_file.read()


def use_template(template_name, output_filepath=None, **kwargs: str):
    """
    Uses a template, formats variables, and writes it to a file.

    Args:
        template_name (str): The name of the template to use.
        output_filepath (str, optional): The filepath to save the output file. If not provided, it will be written to `template_name` in the current working directory.
        **kwargs (str, optional): Keyword arguments to fill in the template variables.

    Raises:
        FileNotFoundError: If the template file is not found.
        IOError: If there is an error writing the output file.

    Examples:
        use_template("submit_slurm.sh", output_filepath="./submit_slurm.sh", PIPELINE="CCBR_nxf", MODULES="ccbrpipeliner nextflow", ENV_VARS="", RUN_COMMAND="nextflow run main.nf -stub")
    """
    template_str = read_template(template_name)
    if not output_filepath:
        output_filepath = template_name
    with open(output_filepath, "wt") as outfile:
        outfile.write(template_str.format(**kwargs))


def use_quarto_ext(ext_name):
    """
    Use a Quarto extension

    Args:
        ext_name (str): The name of the extension in ccbr_tools

    Examples:
        >>> use_quarto_ext("fnl")
    """
    template_files = importlib.resources.files(__package__)
    ext_dir = pathlib.Path("_extensions")
    if not ext_dir.exists():
        ext_dir.mkdir()
    template_dir = template_files / "_extensions" / ext_name
    shutil.copytree(template_dir, ext_dir / ext_name)
    print(f"Copied {ext_name} to {ext_dir}")
