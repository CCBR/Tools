"""
Detect absolute file paths
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


def detect_absolute_paths(files):
    """
    Detect absolute paths in the given files
    """
    detected = sum([file_contains_absolute_path(file) for file in files])
    return detected


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def main(files):
    return detect_absolute_paths(files)


if __name__ == "__main__":
    main()
