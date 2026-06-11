"""
Synchronize `manifest.version` in `nextflow.config` with the repo `VERSION` file.

Whenever the `VERSION` file is updated, the `manifest.version` entry in `nextflow.config` will be updated to match it.

## Usage with pre-commit

Add this to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/CCBR/Tools
  rev: v0.7.0
  hooks:
    - id: sync-nextflow-version
```
"""

import re
from pathlib import Path

import click

MANIFEST_BLOCK_PATTERN = re.compile(r"^\s*manifest\s*\{\s*(?://.*)?$")
MANIFEST_VERSION_PATTERN = re.compile(r"^(\s*version\s*=\s*)(.*?)(\s*(?://.*)?)$")


def update_manifest_version(config_text: str, version: str) -> tuple[str, bool]:
    """
    Update `manifest.version` in a nextflow config string.

    Args:
        config_text: Text from a `nextflow.config` file.
        version: Version string to write into `manifest.version`.

    Returns:
        A tuple containing the updated config text and whether the text changed.

    Raises:
        ValueError: If the config does not contain `manifest.version`.
    """
    lines = config_text.splitlines(keepends=True)
    updated_lines = []
    in_manifest = False
    manifest_depth = 0
    found_manifest_version = False
    changed = False

    for line in lines:
        line_content = line.rstrip("\r\n")
        newline = line[len(line_content) :]

        if not in_manifest and MANIFEST_BLOCK_PATTERN.match(line_content):
            in_manifest = True

        updated_line = line
        if in_manifest and not found_manifest_version:
            match = MANIFEST_VERSION_PATTERN.match(line_content)
            if match:
                updated_line = f'{match.group(1)}"{version}"{match.group(3)}{newline}'
                found_manifest_version = True
                changed = updated_line != line

        updated_lines.append(updated_line)

        if in_manifest:
            manifest_depth += line_content.count("{") - line_content.count("}")
            in_manifest = manifest_depth > 0

    if not found_manifest_version:
        raise ValueError("Could not find manifest.version in nextflow.config.")

    return "".join(updated_lines), changed


@click.command(name="sync-nextflow-version")
def sync_nextflow_version():
    """
    Synchronize `manifest.version` in repo-root `nextflow.config` with `VERSION`.
    """
    nextflow_config = Path.cwd() / "nextflow.config"
    version_file = Path.cwd() / "VERSION"

    if not nextflow_config.exists():
        click.echo("Skipping sync-nextflow-version: nextflow.config not found.")
    else:
        version = version_file.read_text(encoding="utf-8").strip()
        config_text = nextflow_config.read_text(encoding="utf-8")
        updated_text, changed = update_manifest_version(config_text, version)
        if changed:
            nextflow_config.write_text(updated_text, encoding="utf-8")
            click.echo(f"Updated {nextflow_config.name} manifest.version to {version}.")
