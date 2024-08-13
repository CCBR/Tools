from ccbr_tools.shell import shell_run
from ccbr_tools.pipeline.util import get_hpcname


def test_scripts_help():
    assert "extract value for key from JSON" in shell_run(
        "extract_value_from_json.py --help"
    )


def test_which_vpn():
    which_vpn = shell_run("which_vpn.sh")
    hpc = get_hpcname()
    if hpc == "biowulf":
        assert 'DO NOT RUN THIS ON a BIOWULF interactive node!' in which_vpn
    else:
        assert (
            "Are you really connected to VPN?? Doesn't look like it!" in which_vpn
            or "Your VPN IP is" in which_vpn
        )
