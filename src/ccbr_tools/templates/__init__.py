"""
Template files for CCBR Tools.

### Templates

- `submit_slurm.sh` -- slurm submission script template
- `mkdocs-fnl` - theme for websites built with mkdocs material.
- `pkgdown-fnl` - theme for R package websites built with pkgdown.

### Quarto extensions

#### fnl

Quarto HTML format with FNL branding guidelines

First run `ccbr_tools quarto-add fnl` (which runs `quarto use template CCBR/quarto-fnl`), then modify your `_quarto.yml` file with the following:

```yaml
website:
...
page-footer:
    background: black
    foreground: white
    center: |
        Created by the
        [CCR Collaborative Bioinformatics Resource](https://github.com/CCBR)

format: fnl-html
```
"""

import importlib.resources
import subprocess


def read_template(template_name):
    """
    Read a template file

    Args:
        template_name (str): Name of the template file

    Returns:
        template (str): Contents of the template file

    Examples:
        >>> read_template("submit_slurm.sh")
    """

    template_files = importlib.resources.files(__package__)
    template_path = template_files / template_name
    with open(template_path, "rt") as template_file:
        template = template_file.read()
    return template


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
       >>> use_template("submit_slurm.sh", output_filepath="./submit_slurm.sh", MEMORY='1G', WALLTIME="1-00:00:00", PIPELINE="CCBR_nxf", MODULES="ccbrpipeliner nextflow", ENV_VARS="", RUN_COMMAND="nextflow run main.nf -stub")
    """
    template_str = read_template(template_name)
    if not output_filepath:
        output_filepath = template_name
    with open(output_filepath, "wt") as outfile:
        outfile.write(template_str.format(**kwargs))


def get_quarto_extensions():
    """
    List quarto extensions in this package

    Returns:
        extensions (list): List of quarto extension names to use with [](`~ccbr_tools.templates.use_quarto_ext`)

    Examples:
        ```{python}
        from ccbr_tools.templates import get_quarto_extensions
        get_quarto_extensions()
        ```
    """
    ext_dir = importlib.resources.files(__package__) / "_extensions"
    quarto_extensions = ext_dir.glob("*/_extension.yml")
    return [ext.parent.name for ext in quarto_extensions]


def use_quarto_ext(ext_name):
    """
    Use a Quarto extension from the CCBR GitHub organization.

    Runs `quarto use template CCBR/quarto-{ext_name}`.

    Args:
        ext_name (str): The name of the Quarto extension (e.g. "fnl" for CCBR/quarto-fnl).

    Raises:
        subprocess.CalledProcessError: If the quarto command fails.

    Examples:
        >>> use_quarto_ext("fnl")
    """
    subprocess.run(
        ["quarto", "use", "template", f"CCBR/quarto-{ext_name}"],
        check=True,
    )
