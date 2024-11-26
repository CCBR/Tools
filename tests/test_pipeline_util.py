from ccbr_tools.pipeline.util import get_tmp_dir, _get_file_mtime


def test_tmp_dir():
    assert all(
        [
            get_tmp_dir("", "./out", hpc="biowulf").startswith("/lscratch"),
            get_tmp_dir("", "./out", hpc="frce").startswith("./out"),
            get_tmp_dir("", "./out", hpc="none") == None,
        ]
    )


def test_get_mtime():
    mtime = _get_file_mtime("tests/data/file.txt")
    assert all([len(mtime) == 12, mtime.isdigit()])
