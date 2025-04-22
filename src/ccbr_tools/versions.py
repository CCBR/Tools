"""
Get information from git tags, commit hashes, and GitHub releases.
"""

import json
import re
from .shell import shell_run


def get_current_hash():
    """
    Get the current commit hash.

    Uses git rev-parse HEAD to get the current commit hash.

    Returns:
            str: The current commit hash.

    See Also:
        [](`~ccbr_actions.versions.get_latest_release_hash`) : Get the commit hash of the latest release.

    Examples:
        >>> get_current_hash()
        'abc123def4567890abcdef1234567890abcdef12'
    """
    return shell_run("git rev-parse HEAD").strip()


def match_semver(
    version_str,
    with_leading_v=False,
    pattern=r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?",
):
    """
    Match a version string against the semantic versioning pattern.

    See the semantic versioning guidelines: <https://semver.org/>

    Args:
        version_str (str): The version string to match against the semantic versioning pattern.
        with_leading_v (bool): If True, the version string is expected to start with a leading 'v'.
        re.Match or None: The match object if the version string matches the semantic versioning pattern, otherwise None.

    Returns:
        re.Match or None
            The match object if the version string matches the semantic versioning pattern, otherwise None.

    See Also:
        [](`~ccbr_actions.versions.get_major_minor_version`) : Extract the major and minor version from a semantic versioning string.

    Examples:
        >>> match_semver("1.0.0")
        <re.Match object; span=(0, 5), match='1.0.0'>
        >>> match_semver("1.0.0-alpha+001")
        <re.Match object; span=(0, 13), match='1.0.0-alpha+001'>
        >>> match_semver("invalid_version")
        None
    """
    if with_leading_v:
        pattern = f"v{pattern}"
    semver_match = re.match(pattern, version_str)
    if not semver_match:
        # use relaxed version with only major & minor components
        relaxed_pattern = r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)"
        if with_leading_v:
            relaxed_pattern = f"v{relaxed_pattern}"
        semver_match = re.match(relaxed_pattern, version_str)
    return semver_match


def get_major_minor_version(version_str, with_leading_v=False):
    """
    Extract the major and minor version from a semantic versioning string.

    See the semantic versioning guidelines: <https://semver.org/>

    Args:
        version_str (str): The version string to extract from.
        with_leading_v (bool): Whether to include a leading 'v' in the output.

    Returns:
        str or None: The major and minor version in the format 'major.minor', or None if the version string is invalid.

    See Also:
        [](`~ccbr_actions.versions.match_semver`): Match a version string against the semantic versioning pattern.

    Examples:
        >>> get_major_minor_version("1.0.0")
        '1.0'
        >>> get_major_minor_version("2.1.3-alpha")
        '2.1'
        >>> get_major_minor_version("invalid_version")
        None
    """
    semver_match = match_semver(version_str, with_leading_v=with_leading_v)
    prefix = "v" if with_leading_v else ""
    return (
        f"{prefix}{semver_match.group('major')}.{semver_match.group('minor')}"
        if semver_match
        else None
    )


def check_version_increments_by_one(
    current_version,
    next_version,
    with_leading_v=False,
    error_on_false=True,
    debug=False,
):
    """
    Checks if the next version increments by exactly 1 digit from the current version.

    Ensures that the next version follows semantic versioning guidelines
    and increments only one of the major, minor, or patch numbers by 1.

    Args:
        current_version (str): The current version string.
        next_version (str): The proposed next version string.
        with_leading_v (bool, optional): If True, expects the version strings to start with 'v'. Defaults to False.
        error_on_false (bool, optional): If True, raises a ValueError when the check fails. Defaults to True.
        debug (bool, optional): If True, prints debug information. Defaults to False.

    Returns:
        bool: True if the next version increments by exactly one, False otherwise.

    Raises:
        ValueError: If the next version does not match semantic versioning guidelines or does not increment by exactly one.

    Examples:
        >>> check_version_increments_by_one("1.0.0", "1.0.1")
        True
        >>> check_version_increments_by_one("1.0.0", "1.1.0")
        True
        >>> check_version_increments_by_one("1.0.0", "2.0.0")
        True
        >>> check_version_increments_by_one("1.0.0", "1.0.2")
        False
        >>> check_version_increments_by_one("1.0.0", "1.2.0")
        False
        >>> check_version_increments_by_one("1.0.0", "3.0.0")
        False
    """
    is_valid = True
    error_msg = f"Next version must only increment one number at a time. Current version: {current_version}. Proposed next version: {next_version}."
    # assert semantic version pattern
    next_semver = match_semver(next_version, with_leading_v=with_leading_v)
    if not next_semver:
        extra_msg = ""
        if with_leading_v and not next_version.startswith("v"):
            extra_msg = "The tag does not start with 'v'."
        raise ValueError(
            f"Tag {next_version} does not match semantic versioning guidelines. {extra_msg}\nView the guidelines here: https://semver.org/"
        )

    # assert next version is only 1 greater than current
    current_semver = match_semver(current_version, with_leading_v=with_leading_v)

    groups = ["major", "minor", "patch"]

    groups_by_one = {
        grp: (int(next_semver.group(grp)) == 1 + int(current_semver.group(grp)))
        for grp in groups
    }
    groups_equal = {
        grp: (int(next_semver.group(grp)) == int(current_semver.group(grp)))
        for grp in groups
    }
    num_greater = sum(groups_by_one.values())
    if debug:
        print("group_increments: ", groups_by_one)
        print("group_equals: ", groups_equal)
    # if a digit is not incremented, it must be equal
    bigger_digit_increments = False
    for grp in groups:
        increments = groups_by_one[grp]
        equals = groups_equal[grp]
        if not increments and not (
            equals or (int(next_semver.group(grp)) == 0) and bigger_digit_increments
        ):
            is_valid = False
            if error_on_false:
                raise ValueError(error_msg)
        if increments:
            bigger_digit_increments = True
    # must increment by exactly one
    if not (num_greater == 1):
        is_valid = False
        if error_on_false:
            raise ValueError(error_msg)

    return is_valid


def is_ancestor(ancestor, descendant):
    """
    Check if one commit is an ancestor of another.

    Uses git merge-base --is-ancestor to determine if the ancestor is an ancestor of the descendant.

    Args:
        ancestor (str): The commit hash of the potential ancestor.
        descendant (str): The commit hash of the potential descendant.

    Returns:
        bool: True if the ancestor is an ancestor of the descendant, otherwise False.

    See Also:
        [](`~ccbr_actions.versions.get_latest_release_hash`) : Get the commit hash of the latest release.
        [](`~ccbr_actions.versions.get_current_hash`) : Get the commit hash of the current.

    Examples:
        >>> is_ancestor("abc123", "def456")
        True
        >>> is_ancestor("abc123", "ghi789")
        False
    """
    return bool(
        shell_run(
            f"git merge-base --is-ancestor {ancestor} {descendant} && echo True || echo False"
        ).strip()
    )


def get_releases(limit=1, args="", json_fields="name,tagName,isLatest,publishedAt"):
    """
    Get a list of releases from GitHub.

    Uses the GitHub CLI to retrieve a list of releases from a repository.
    You will need to [install it](https://cli.github.com/) before you can use this function.

    Args:
        limit (int, optional): The maximum number of releases to retrieve (default is 1).
        args (str, optional): Additional arguments to pass to the GitHub CLI command (default is "").
        json_fields (str, optional): The JSON fields to include in the output (default is "name,tagName,isLatest,publishedAt").

    Returns:
        list: A list of dictionaries containing release information.

    See Also:
        [](`~ccbr_actions.versions.get_latest_release_tag`) : Get the tag name of the latest release.
        [](`~ccbr_actions.versions.get_latest_release_hash`) : Get the commit hash of the latest release.

    Notes:
        gh cli docs: <https://cli.github.com/manual/gh_release_list>

    Examples:
        >>> get_releases(limit=2)
        [{'name': 'v1.0.0', 'tagName': 'v1.0.0', 'isLatest': True, 'publishedAt': '2021-01-01T00:00:00Z'},
        {'name': 'v0.9.0', 'tagName': 'v0.9.0', 'isLatest': False, 'publishedAt': '2020-12-01T00:00:00Z'}]
        >>> get_releases(limit=2, args="--repo CCBR/RENEE")
        [{'isLatest': True, 'name': 'RENEE 2.5.12', 'publishedAt': '2024-04-12T14:49:11Z', 'tagName': 'v2.5.12'},
        {'isLatest': False, 'name': 'RENEE 2.5.11', 'publishedAt': '2024-01-22T21:02:30Z', 'tagName': 'v2.5.11'}]
    """
    releases = shell_run(f"gh release list --limit {limit} --json {json_fields} {args}")
    return json.loads(releases)


def get_latest_release_tag(args=""):
    """
    Get the tag name of the latest release.

    Uses the GitHub CLI to retrieve the latest release tag from a repository.

    Args:
        args (str, optional): Additional arguments to pass to the GitHub CLI command (default is "").

    Returns:
        str or None: The tag name of the latest release, or None if no latest release is found.

    See Also:
        [](`~ccbr_actions.versions.get_releases`): Get a list of releases from GitHub.

    Examples:
        >>> get_latest_release_tag()
        'v1.0.0'
    """
    releases = get_releases(limit=100, args=args)
    latest_release = next(
        (release for release in releases if release["isLatest"]), None
    )
    return latest_release["tagName"] if latest_release else ""


def get_latest_release_hash(args=""):
    """
    Get the commit hash of the latest release.

    Uses git rev-list to get the commit hash of the latest release tag.

    Args:
        args (str, optional): Additional arguments to pass to the GitHub CLI command (default is "").

    Returns:
        str: The commit hash of the latest release.

    Raises:
        ValueError: If the tag is not found in the repository commit history.

    See Also:
        [](`~ccbr_actions.versions.get_latest_release_tag`): Get the tag name of the latest release.

    Examples:
        >>> get_latest_release_hash()
        'abc123def4567890abcdef1234567890abcdef12'
    """
    tag_name = get_latest_release_tag(args=args)
    tag_hash = ""
    if tag_name:
        tag_hash = shell_run(f"git rev-list -n 1 {tag_name}")
        if "fatal: ambiguous argument" in tag_hash:
            raise ValueError(f"Tag {tag_name} not found in repository commit history")
    return tag_hash.strip()
