"""
Detect absolute file paths

Any instances of absolute paths (i.e. paths starting with "/") in the given files will be detected and printed to the console, and an error will be raised at the end if any are found.

## Usage with pre-commit

Add this to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/CCBR/Tools
  rev: v0.5.0
  hooks:
    - id: detect-absolute-paths
```

## Ignoring specific lines

You can ignore specific lines by including the string "abs-path:ignore" in the line, e.g.:
```python
some_path = "/absolute/path/to/file" # abs-path:ignore
```

"""

import click


def line_contains_absolute_path(line):
    """
    Detect absolute paths in a line of text
    """
    return any([word.startswith("/") for word in line.split()])


def line_contains_ignore(line):
    """
    Detect if a line contains the string "abs-path:ignore"
    """
    return "abs-path:ignore" in line


def file_contains_absolute_path(file):
    """
    Detect absolute paths in a file
    """
    detected = False
    with open(file, "r") as f:
        for line in f:
            if not line_contains_ignore(line) and line_contains_absolute_path(line):
                print(f"Absolute path detected in {file}: {line.strip()}")
                detected = True
    return detected


def raise_error_if_abs_paths_detected(files):
    """
    Raise an error if absolute paths are detected in the given files
    """
    if any([file_contains_absolute_path(file) for file in files]):
        raise click.ClickException("Absolute paths detected in the above files.")


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def detect_absolute_paths(files):
    """
    Detect absolute file paths in the given files and raise an error if any are found.
    """
    raise_error_if_abs_paths_detected(files)


if __name__ == "__main__":
    detect_absolute_paths()
