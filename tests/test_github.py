from ccbr_tools.github import print_contributor_images, get_user_info
import pytest


def test_print_contributor_images():
    assert not print_contributor_images(repo="actions", org="CCBR")


def test_print_contributor_images_skips_apps(mocker):
    """Test that print_contributor_images skips GitHub app contributors"""
    # Mock contributors including both a regular user and an app
    mock_contributors = [
        {
            "login": "user1",
            "avatar_url": "https://avatars.githubusercontent.com/u/123",
            "html_url": "https://github.com/user1",
        },
        {
            "login": "dependabot[bot]",
            "avatar_url": "https://avatars.githubusercontent.com/in/29110",
            "html_url": "https://github.com/apps/dependabot",
        },
        {
            "login": "user2",
            "avatar_url": "https://avatars.githubusercontent.com/u/456",
            "html_url": "https://github.com/user2",
        },
    ]

    # Mock user info for regular users
    mock_user_info = {
        "user1": {"login": "user1", "name": "User One"},
        "user2": {"login": "user2", "name": "User Two"},
    }

    mocker.patch(
        "ccbr_tools.github.get_repo_contributors", return_value=mock_contributors
    )
    mock_get_user_info = mocker.patch("ccbr_tools.github.get_user_info")
    mock_print = mocker.patch("builtins.print")

    mock_get_user_info.side_effect = lambda login: mock_user_info.get(
        login, {"login": login, "name": None}
    )

    print_contributor_images(repo="test-repo", org="test-org")

    # Should only print HTML for the 2 regular users, not the app
    assert mock_print.call_count == 2

    # Verify that the app contributor was NOT printed
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert not any("dependabot" in call for call in printed_calls)
    assert not any("github.com/apps" in call for call in printed_calls)

    # Verify that regular users were printed
    assert any("User One" in call for call in printed_calls)
    assert any("User Two" in call for call in printed_calls)


def test_get_user_info_not_found(mocker):
    """Test that get_user_info handles ConnectionError gracefully"""
    # Mock get_url_json to raise a ConnectionError
    mock_get_url_json = mocker.patch("ccbr_tools.github.get_url_json")
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
