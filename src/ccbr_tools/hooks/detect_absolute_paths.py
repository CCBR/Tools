"""
Detect absolute file paths

Any instances of absolute paths (i.e. paths starting with "/") in the given files will be detected and printed to the console (unless "abs-path:ignore" is included).
An error will be raised at the end if any are found.

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

## Ignoring specific files

You can ignore files using gitignore-style patterns:

Via CLI:
```bash
detect-absolute-paths file1.txt file2.log --ignore-paths "*.log"
detect-absolute-paths **/*.txt --ignore-paths "*.log" --ignore-paths "test_*.py"
```

Via ignore file:
```bash
detect-absolute-paths **/*.txt --ignore-paths-file .abs-ignore
```

"""

import mimetypes

import click
import pathspec


def word_is_absolute_path(word):
    """
    Detect if a word starts with a slash (indicating an absolute path)

    Standalone / and // are not considered absolute paths as they are often used
    in pathlib to delimited paths and as comments in groovy/nextflow
    """
    word = word.strip().lstrip("([{").rstrip(",:;)]}").strip("'\"")

    return word.startswith("/") and not any(
        [
            word == "/",  # FP from pathlib. abs-path:ignore
            word.startswith("//"),  # FP from groovy comments. abs-path:ignore
            word == "/*",  # FP from multiline groovy comments. abs-path:ignore
            word.startswith("/*--"),  # FP from CSS comments. abs-path:ignore
            word == "/$",  # FP from nextflow scripts. abs-path:ignore
        ]
    )


def line_contains_absolute_path(line):
    """
    Detect absolute paths in a line of text
    """
    return any([word_is_absolute_path(word) for word in line.split()])


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
    if file_is_text(file):
        with open(file, "r") as f:
            for line in f:
                if not line_contains_ignore(line) and line_contains_absolute_path(line):
                    print(f"Absolute path detected in {file}: {line.strip()}")
                    detected = True
    return detected


def raise_error_if_abs_paths_detected(files, ignored_patterns=None):
    """
    Raise an error if absolute paths are detected in the given files
    """
    if ignored_patterns:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", ignored_patterns)
        files = [file for file in files if not spec.match_file(file)]

    if any([file_contains_absolute_path(file) for file in files]):
        raise click.ClickException("Absolute paths detected in the above files.")


def load_ignored_paths(ignored_paths_file):
    """
    Load ignored file paths/patterns from a file, one per line.
    Supports gitignore-style wildcards.
    """
    if not ignored_paths_file:
        return []

    patterns = []
    with open(ignored_paths_file, "r") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            patterns.append(stripped)

    return patterns


def file_is_text(file):
    """
    Detect whether a file is likely text based on its MIME type.
    """
    mime_type, _ = mimetypes.guess_type(str(file))
    return mime_type is None or mime_type.startswith("text/")


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--ignore-paths-file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help="Optional file with file patterns to ignore (gitignore-style, one per line).",
)
@click.option(
    "--ignore-paths",
    multiple=True,
    help="File patterns to ignore (gitignore-style). Can be specified multiple times.",
)
def detect_absolute_paths(files, ignore_paths_file, ignore_paths):
    """
    Detect absolute file paths in the given files and raise an error if any are found.
    """
    patterns = list(ignore_paths) if ignore_paths else []
    patterns.extend(load_ignored_paths(ignore_paths_file))
    raise_error_if_abs_paths_detected(files, patterns)


if __name__ == "__main__":
    detect_absolute_paths()
