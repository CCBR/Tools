from ccbr_tools.pkg_util import repo_base, get_url_json
import pytest


def test_repo_base():
    assert str(repo_base()).endswith("ccbr_tools")


def test_get_url_json():
    with pytest.raises(ConnectionError) as exc_info:
        url = "https://api.github.com/users/"
        get_url_json(url)
    assert (
        str(exc_info.value)
        == "Failed to fetch data from https://api.github.com/users/. Request failed with status code 404."
    )
