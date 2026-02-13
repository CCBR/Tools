from ccbr_tools.github import print_contributor_images, get_user_info
import pytest
import warnings
from unittest.mock import patch


def test_print_contributor_images():
    assert not print_contributor_images(repo="actions", org="CCBR")


def test_get_user_info_not_found():
    """Test that get_user_info handles ConnectionError gracefully"""
    # Mock get_url_json to raise a ConnectionError
    with patch("ccbr_tools.github.get_url_json") as mock_get_url_json:
        mock_get_url_json.side_effect = ConnectionError(
            "Failed to fetch data from https://api.github.com/users/nonexistent. Request failed with status code 404."
        )

        # Should issue a warning but not raise an exception
        with pytest.warns(UserWarning) as record:
            result = get_user_info("nonexistent")

        # Should return a minimal dict with login and name=None
        assert result["login"] == "nonexistent"
        assert result["name"] is None

        # Should have issued a warning
        assert len(record) == 1
        assert "Could not retrieve user info" in str(record[0].message)
