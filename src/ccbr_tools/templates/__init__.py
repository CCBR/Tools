"""
Template files for CCBR Tools.

### Templates

- `submit_slurm.sh` -- slurm submission script template
- `mkdocs-fnl` - theme for websites built with mkdocs material.
- `pkgdown-fnl` - theme for R package websites built with pkgdown.

### Quarto extensions

#### fnl

Quarto HTML format with FNL branding guidelines

First run `ccbr_tools quarto-add fnl`, then modify your `_quarto.yml` file with the following:

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
import pathlib
import shutil


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
       >>> use_template("submit_slurm.sh", output_filepath="./submit_slurm.sh", PIPELINE="CCBR_nxf", MODULES="ccbrpipeliner nextflow", ENV_VARS="", RUN_COMMAND="nextflow run main.nf -stub")
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
    Use a Quarto extension

    Args:
        ext_name (str): The name of the extension in ccbr_tools

    Examples:
        >>> use_quarto_ext("fnl")
    """
    ext_dir = importlib.resources.files(__package__) / "_extensions"
    template_dir = ext_dir / ext_name
    if not template_dir.exists() and not (template_dir / "_extension.yml").is_file():
        raise FileNotFoundError(
            f"{ext_name} does not exist. Available extensions: {', '.join(get_quarto_extensions())}"
        )
    out_dir = pathlib.Path("_extensions")
    if not out_dir.exists():
        out_dir.mkdir()
    shutil.copytree(template_dir, out_dir / ext_name, dirs_exist_ok=True)
    print(f"Copied {ext_name} to {out_dir}")
