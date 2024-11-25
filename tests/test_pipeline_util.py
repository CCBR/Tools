from ccbr_tools.pipeline.util import get_tmp_dir


def test_tmp_dir():
    assert all(
        [
            get_tmp_dir("", "./out", hpc="biowulf").startswith("/lscratch"),
            get_tmp_dir("", "./out", hpc="frce").startswith("./out"),
            get_tmp_dir("", "./out", hpc="none") == None,
        ]
    )
