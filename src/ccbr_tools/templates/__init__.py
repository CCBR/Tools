"""
Template files for CCBR Tools.

Templates:
    - `ccbr_tools.templates.submit_slurm.sh`
"""

import importlib.resources


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


def use_template(template_name, output_filepath=None, **kwargs):
    """
    Uses a template, formats variables, and writes it to a file.

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
