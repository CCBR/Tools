from ccbr_tools.github import print_contributor_images


def test_print_contributor_images():
    assert not print_contributor_images(repo="actions", org="CCBR")
