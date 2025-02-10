"""
GitHub helper functions

Contributor related functions:

- [](`~ccbr_tools.github.print_contributor_images`) - Print contributor profile images for HTML web pages
- [](`~ccbr_tools.github.get_repo_contributors`) - Get a list of contributors to a GitHub repository
- [](`~ccbr_tools.github.get_user_info`) - Get profile information about a GitHub user
- [](`~ccbr_tools.github.get_contrib_html`) - Generates HTML for a GitHub contributor's profile image and link
"""

from .pkg_util import get_url_json


def print_contributor_images(repo, org="CCBR"):
    """
    Print contributor profile images for HTML web pages

    Args:
        repo (str): The name of the GitHub repository.
        org (str): The GitHub organization or user that owns the repository. Defaults to 'CCBR'.

    Returns:
        None
    """
    contribs = get_repo_contributors(repo, org)
    for contrib in contribs:
        print(get_contrib_html(contrib))


def get_repo_contributors(repo, org="CCBR"):
    """
    Get a list of contributors to a GitHub repository.

    Args:
        repo (str): The name of the repository.
        org (str, optional): The organization name. Defaults to 'CCBR'.
    Returns:
        list: A list of contributors to the specified repository.
    """
    url = f"https://api.github.com/repos/{org}/{repo}/contributors"
    return get_url_json(url)


def get_user_info(user_login):
    """
    Get profile information about a GitHub user.

    Args:
        user_login (str): The GitHub username of the user.

    Returns:
        dict: A dictionary containing the user's profile information.
    """
    url = f"https://api.github.com/users/{user_login}"
    return get_url_json(url)


def get_contrib_html(contrib, img_attr="{width=100px height=100px}"):
    """
    Generates HTML for a GitHub contributor's profile image and link.

    Args:
        contrib (dict): A dictionary containing contributor information.
                        Expected keys are 'login', 'avatar_url', and 'html_url'.

    Returns:
        str: A string containing HTML that displays the contributor's profile image
             and links to their GitHub profile.
    """
    user_login = contrib["login"]
    user_info = get_user_info(user_login)
    user_name = user_info["name"] if user_info["name"] else user_login
    avatar_url = contrib["avatar_url"]
    profile_url = contrib["html_url"]
    return f"[![{user_name}]({avatar_url})]({profile_url}){img_attr}\n"
