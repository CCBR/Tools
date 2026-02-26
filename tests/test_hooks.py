import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from ccbr_tools.hooks import detect_absolute_paths as hooks
import ccbr_tools.hooks.__main__ as hooks_main


def test_line_contains_absolute_path():
    assert hooks.line_contains_absolute_path("/tmp/file")
    assert not hooks.line_contains_absolute_path("relative/path")


def test_line_contains_ignore():
    assert hooks.line_contains_ignore("value # abs-path:ignore")
    assert not hooks.line_contains_ignore("no ignore tag")


def test_file_contains_absolute_path_reports(tmp_path, capsys):
    target = tmp_path / "sample.txt"
    target.write_text("/tmp/file\n", encoding="utf-8")

    assert hooks.file_contains_absolute_path(target)

    captured = capsys.readouterr()
    assert "Absolute path detected in" in captured.out


def test_file_contains_absolute_path_ignores_tag(tmp_path, capsys):
    target = tmp_path / "sample.txt"
    target.write_text("/tmp/file # abs-path:ignore\n", encoding="utf-8")

    assert not hooks.file_contains_absolute_path(target)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_raise_error_if_abs_paths_detected(tmp_path):
    with_abs = tmp_path / "with_abs.txt"
    with_abs.write_text("/tmp/file\n", encoding="utf-8")

    without_abs = tmp_path / "without_abs.txt"
    without_abs.write_text("relative/path\n", encoding="utf-8")

    with pytest.raises(hooks.click.ClickException):
        hooks.raise_error_if_abs_paths_detected([with_abs, without_abs])

    hooks.raise_error_if_abs_paths_detected([without_abs])


def test_detect_absolute_paths_cli(tmp_path):
    runner = CliRunner()

    with_abs = tmp_path / "with_abs.txt"
    with_abs.write_text("/tmp/file\n", encoding="utf-8")

    without_abs = tmp_path / "without_abs.txt"
    without_abs.write_text("relative/path\n", encoding="utf-8")

    result = runner.invoke(hooks.detect_absolute_paths, [str(with_abs)])
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output

    result = runner.invoke(hooks.detect_absolute_paths, [str(without_abs)])
    assert result.exit_code == 0
    assert result.output == ""


def test_detect_absolute_paths_lscratch_line():
    target = Path(__file__).resolve().parent / "data" / "hooks" / "abs-path.txt"
    assert hooks.file_contains_absolute_path(target)


def test_hooks_cli_help():
    runner = CliRunner()

    result = runner.invoke(hooks_main.cli, ["--help"])

    assert result.exit_code == 0
    assert "Pre-commit hooks for CCBR Bioinformatics Software" in result.output


def test_hooks_cli_callback_smoke():
    assert hooks_main.cli.callback() is None


def test_hooks_main_invokes_cli(mocker):
    mock_cli = mocker.patch.object(hooks_main, "cli")

    hooks_main.main()

    mock_cli.assert_called_once_with(prog_name="ccbr-hooks")


def test_hooks_main_module_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ccbr-hooks", "--help"])
    sys.modules.pop("ccbr_tools.hooks.__main__", None)

    try:
        runpy.run_module("ccbr_tools.hooks.__main__", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0


def test_pre_commit_try_repo_detect_absolute_paths(tmp_path):
    if shutil.which("pre-commit") is None:
        pytest.skip("pre-commit is not installed")

    repo_root = tmp_path

    with_abs = repo_root / "with_abs.txt"
    with_abs.write_text("/tmp/file\n", encoding="utf-8")

    without_abs = repo_root / "without_abs.txt"
    without_abs.write_text("relative/path\n", encoding="utf-8")

    tools_repo = str(Path(__file__).resolve().parents[1])

    result = subprocess.run(
        [
            "pre-commit",
            "try-repo",
            tools_repo,
            "detect-absolute-paths",
            "--files",
            str(with_abs),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Absolute paths detected" in (result.stdout + result.stderr)

    result = subprocess.run(
        [
            "pre-commit",
            "try-repo",
            tools_repo,
            "detect-absolute-paths",
            "--files",
            str(without_abs),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_detect_absolute_paths_module_entrypoint(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["detect-absolute-paths"])

    try:
        runpy.run_path(str(Path(hooks.__file__)), run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
