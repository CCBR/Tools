from ccbr_tools.util import shell_run


def test_help_jobby():
    assert "Will take your job(s)... and display their information!" in shell_run(
        "jobby -h"
    )
