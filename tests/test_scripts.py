from ccbr_tools.util import shell_run


def test_scripts_help():
    assert "extract value for key from JSON" in shell_run(
        "extract_value_from_json.py --help"
    )


def test_which_vpn():
    assert "Are you really connected to VPN?? Doesn't look like it!" in shell_run(
        "which_vpn.sh"
    )
