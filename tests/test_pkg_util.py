from ccbr_tools.pkg_util import repo_base


def test_repo_base():
    assert str(repo_base()).endswith("ccbr_tools")
