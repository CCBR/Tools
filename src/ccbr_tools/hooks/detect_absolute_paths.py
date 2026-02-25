"""
Detect absolute paths
"""

import click


def line_contains_absolute_path(line):
    """
    Detect absolute paths in a line of text
    """
    # TODO more intelligent detection of absolute paths
    return any([word.startswith("/") for word in line.split()])


def file_contains_absolute_path(file):
    """Detect absolute paths in a file"""
    with open(file, "r") as f:
        for line in f:
            if line_contains_absolute_path(line):
                print(f"Absolute path detected in {file}: {line.strip()}")
                return True
    return False


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
