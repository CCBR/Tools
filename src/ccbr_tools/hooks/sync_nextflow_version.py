"""
Synchronize `manifest.version` in `nextflow.config` with the repo `VERSION` file.

## Usage with pre-commit

Add this to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/CCBR/Tools
  rev: v0.5.0
  hooks:
    - id: sync-nextflow-version
```
"""

import re
from pathlib import Path

import click

MANIFEST_BLOCK_PATTERN = re.compile(r"^\s*manifest\s*\{\s*(?://.*)?$")
MANIFEST_VERSION_PATTERN = re.compile(r"""^(\s*version\s*=\s*)(['"])[^'"]*(\2)(.*)$""")


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
            manifest_depth = line_content.count("{") - line_content.count("}")

        if in_manifest and not found_manifest_version:
            match = MANIFEST_VERSION_PATTERN.match(line_content)
            if match:
                updated_line = (
                    f"{match.group(1)}{match.group(2)}{version}"
                    f"{match.group(2)}{match.group(4)}{newline}"
                )
                updated_lines.append(updated_line)
                found_manifest_version = True
                changed = updated_line != line
                manifest_depth += line_content.count("{") - line_content.count("}")
                if manifest_depth <= 0:
                    in_manifest = False
                continue

        updated_lines.append(line)

        if in_manifest:
            manifest_depth += line_content.count("{") - line_content.count("}")
            if manifest_depth <= 0:
                in_manifest = False

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
    elif not version_file.exists():
        raise click.ClickException("VERSION file not found at repository root.")
    else:
        version = version_file.read_text(encoding="utf-8").strip()
        config_text = nextflow_config.read_text(encoding="utf-8")
        try:
            updated_text, changed = update_manifest_version(config_text, version)
        except ValueError as error:
            raise click.ClickException(str(error)) from error

        if changed:
            nextflow_config.write_text(updated_text, encoding="utf-8")
            click.echo(
                f"Updated {nextflow_config.name} manifest.version to {version}."
            )
