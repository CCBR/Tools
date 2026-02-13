from ccbr_tools.github import print_contributor_images, get_user_info
import pytest
import warnings


def test_print_contributor_images():
    assert not print_contributor_images(repo="actions", org="CCBR")


def test_get_user_info_not_found():
    """Test that get_user_info handles non-existent users gracefully"""
    # Use a username that is very unlikely to exist
    with pytest.warns(UserWarning) as record:
        result = get_user_info("this-user-definitely-does-not-exist-12345")
    
    # Should return a minimal dict with login and name=None
    assert result["login"] == "this-user-definitely-does-not-exist-12345"
    assert result["name"] is None
    
    # Should have issued a warning
    assert len(record) == 1
    assert "Could not retrieve user info" in str(record[0].message)
