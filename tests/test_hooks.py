import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from ccbr_tools.hooks import detect_absolute_paths as hooks
import ccbr_tools.hooks.__main__ as hooks_main


def test_word_is_absolute_path():
    # Basic absolute paths
    assert hooks.word_is_absolute_path("/tmp/file")
    assert hooks.word_is_absolute_path("/usr/local/bin")
    assert hooks.word_is_absolute_path("/home/user/data")

    # Absolute paths with quotes and punctuation
    assert hooks.word_is_absolute_path("'/tmp/file'")
    assert hooks.word_is_absolute_path('"/tmp/file"')
    assert hooks.word_is_absolute_path("(/tmp/file)")
    assert hooks.word_is_absolute_path("[/tmp/file]")
    assert hooks.word_is_absolute_path("{/tmp/file}")
    assert hooks.word_is_absolute_path("/tmp/file,")
    assert hooks.word_is_absolute_path("/tmp/file;")

    # Not absolute paths
    assert not hooks.word_is_absolute_path("relative/path")
    assert not hooks.word_is_absolute_path("./relative/path")
    assert not hooks.word_is_absolute_path("../relative/path")
    assert not hooks.word_is_absolute_path("file.txt")

    # Edge cases that should NOT be detected as absolute paths
    assert not hooks.word_is_absolute_path("/")  # pathlib delimiter
    assert not hooks.word_is_absolute_path("//")  # groovy comments
    assert not hooks.word_is_absolute_path("/*")  # groovy multiline comments
    assert not hooks.word_is_absolute_path("/*--")  # CSS comments
    assert not hooks.word_is_absolute_path("/dev/null")  # common shell redirection
    assert not hooks.word_is_absolute_path("/dev/shm")  # common shell redirection
    assert not hooks.word_is_absolute_path("/$")  # nextflow script


def test_line_contains_absolute_path():
    assert hooks.line_contains_absolute_path("/tmp/file")
    assert not hooks.line_contains_absolute_path("relative/path")

    # Test with multiple words
    assert hooks.line_contains_absolute_path("some text /tmp/file more text")
    assert not hooks.line_contains_absolute_path("some text relative/path more text")

    # Test with quotes
    assert hooks.line_contains_absolute_path('path = "/tmp/file"')
    assert hooks.line_contains_absolute_path("path = '/tmp/file'")


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


def test_load_ignored_paths_returns_empty_for_none():
    result = hooks.load_ignored_paths(None)
    assert result == []


def test_load_ignored_paths_loads_patterns(tmp_path):
    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text(
        "# This is a comment\n"
        "*.log\n"
        "docs/*.md\n"
        "\n"  # blank line
        "**/test_*.py\n"
        "build/\n",
        encoding="utf-8",
    )

    patterns = hooks.load_ignored_paths(ignore_file)
    assert len(patterns) == 4
    assert "*.log" in patterns
    assert "docs/*.md" in patterns
    assert "**/test_*.py" in patterns
    assert "build/" in patterns
    assert "# This is a comment" not in patterns


def test_raise_error_if_abs_paths_detected_with_ignored_patterns(tmp_path):
    # Create test files
    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    file3 = tmp_path / "file3.txt"
    file3.write_text("relative/path\n", encoding="utf-8")

    # Should raise error when file2.txt has absolute path
    with pytest.raises(hooks.click.ClickException):
        hooks.raise_error_if_abs_paths_detected([file1, file2, file3])

    # Should NOT raise error when file1.log is ignored (*.log pattern)
    hooks.raise_error_if_abs_paths_detected([file1, file3], ignored_patterns=["*.log"])

    # Should still raise error for file2.txt even with *.log pattern
    with pytest.raises(hooks.click.ClickException):
        hooks.raise_error_if_abs_paths_detected(
            [file1, file2, file3], ignored_patterns=["*.log"]
        )


def test_raise_error_if_abs_paths_detected_with_directory_pattern(tmp_path):
    # Create nested structure
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    build_file = build_dir / "output.txt"
    build_file.write_text("/tmp/file\n", encoding="utf-8")

    src_file = tmp_path / "src.txt"
    src_file.write_text("/tmp/file\n", encoding="utf-8")

    # Should raise error without ignore
    with pytest.raises(hooks.click.ClickException):
        hooks.raise_error_if_abs_paths_detected([build_file, src_file])

    # Should NOT raise error when build/ is ignored
    with pytest.raises(hooks.click.ClickException):
        # Still fails because src.txt has absolute path
        hooks.raise_error_if_abs_paths_detected(
            [build_file, src_file], ignored_patterns=["build/"]
        )

    # Should pass when only build_file is checked with pattern
    hooks.raise_error_if_abs_paths_detected([build_file], ignored_patterns=["build/**"])


def test_raise_error_if_abs_paths_detected_with_glob_patterns(tmp_path):
    # Create test files
    test1 = tmp_path / "test_foo.py"
    test1.write_text("/tmp/file\n", encoding="utf-8")

    test2 = tmp_path / "test_bar.py"
    test2.write_text("/tmp/file\n", encoding="utf-8")

    main = tmp_path / "main.py"
    main.write_text("/tmp/file\n", encoding="utf-8")

    # Should raise error without ignore
    with pytest.raises(hooks.click.ClickException):
        hooks.raise_error_if_abs_paths_detected([test1, test2, main])

    # Should pass when test_*.py files are ignored
    with pytest.raises(hooks.click.ClickException):
        # Still fails because main.py has absolute path
        hooks.raise_error_if_abs_paths_detected(
            [test1, test2, main], ignored_patterns=["test_*.py"]
        )

    # Should pass when all test files ignored
    hooks.raise_error_if_abs_paths_detected(
        [test1, test2], ignored_patterns=["test_*.py"]
    )


def test_detect_absolute_paths_cli_with_ignore_paths_file(tmp_path):
    runner = CliRunner()

    # Create test files
    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    # Create ignore file
    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text("*.log\n", encoding="utf-8")

    # Should fail without ignore file
    result = runner.invoke(hooks.detect_absolute_paths, [str(file1), str(file2)])
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output

    # Should still fail with ignore file (file2.txt not ignored)
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(file1), str(file2), "--ignore-paths-file", str(ignore_file)],
    )
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output

    # Should pass when only file1.log is checked (it's ignored)
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(file1), "--ignore-paths-file", str(ignore_file)],
    )
    assert result.exit_code == 0


def test_detect_absolute_paths_cli_with_ignore_paths_option(tmp_path):
    runner = CliRunner()

    # Create test files
    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    file3 = tmp_path / "test_foo.py"
    file3.write_text("/tmp/file\n", encoding="utf-8")

    # Should fail without ignore patterns
    result = runner.invoke(hooks.detect_absolute_paths, [str(file1), str(file2)])
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output

    # Should pass when file1.log is ignored via CLI
    result = runner.invoke(
        hooks.detect_absolute_paths, [str(file1), "--ignore-paths", "*.log"]
    )
    assert result.exit_code == 0

    # Should still fail when file2.txt is not ignored
    result = runner.invoke(
        hooks.detect_absolute_paths, [str(file1), str(file2), "--ignore-paths", "*.log"]
    )
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output

    # Should pass when multiple patterns are specified
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [
            str(file1),
            str(file3),
            "--ignore-paths",
            "*.log",
            "--ignore-paths",
            "test_*.py",
        ],
    )
    assert result.exit_code == 0


def test_detect_absolute_paths_cli_with_both_file_and_cli_patterns(tmp_path):
    runner = CliRunner()

    # Create test files
    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    file3 = tmp_path / "test_foo.py"
    file3.write_text("/tmp/file\n", encoding="utf-8")

    # Create ignore file with *.log pattern
    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text("*.log\n", encoding="utf-8")

    # Should pass when combining file and CLI patterns
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [
            str(file1),
            str(file3),
            "--ignore-paths-file",
            str(ignore_file),
            "--ignore-paths",
            "test_*.py",
        ],
    )
    assert result.exit_code == 0

    # Should still detect file2.txt
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [
            str(file1),
            str(file2),
            str(file3),
            "--ignore-paths-file",
            str(ignore_file),
            "--ignore-paths",
            "test_*.py",
        ],
    )
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output


def test_detect_absolute_paths_cli_with_empty_ignore_paths(tmp_path):
    """Test that empty --ignore-paths values are handled correctly"""
    runner = CliRunner()

    file1 = tmp_path / "file1.txt"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    # Should still detect absolute paths when --ignore-paths is provided but empty
    result = runner.invoke(
        hooks.detect_absolute_paths, [str(file1), "--ignore-paths", ""]
    )
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output


def test_detect_absolute_paths_cli_with_directory_patterns(tmp_path):
    """Test --ignore-paths with directory patterns"""
    runner = CliRunner()

    # Create nested directory structure
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    build_file = build_dir / "output.txt"
    build_file.write_text("/tmp/file\n", encoding="utf-8")

    src_file = tmp_path / "src.txt"
    src_file.write_text("/tmp/file\n", encoding="utf-8")

    # Should ignore files in build directory
    result = runner.invoke(
        hooks.detect_absolute_paths, [str(build_file), "--ignore-paths", "build/**"]
    )
    assert result.exit_code == 0

    # Should still detect src.txt
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(build_file), str(src_file), "--ignore-paths", "build/**"],
    )
    assert result.exit_code != 0
    assert "Error: Absolute paths detected" in result.output


def test_ignore_paths_file_with_comments_and_blanks(tmp_path):
    """Test that ignore file handles comments and blank lines correctly"""
    runner = CliRunner()

    file1 = tmp_path / "test.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "data.csv"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    # Create ignore file with comments and blank lines
    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text(
        "# This is a comment\n\n*.log\n\n# Another comment\n*.csv\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(file1), str(file2), "--ignore-paths-file", str(ignore_file)],
    )
    assert result.exit_code == 0


def test_ignore_paths_cli_help(tmp_path):
    """Test that --ignore-paths appears in help text"""
    runner = CliRunner()

    result = runner.invoke(hooks.detect_absolute_paths, ["--help"])
    assert result.exit_code == 0
    assert "--ignore-paths" in result.output
    assert "--ignore-paths-file" in result.output
    assert "gitignore-style" in result.output


def test_ignore_paths_only_cli_no_file(tmp_path):
    """Test --ignore-paths works without --ignore-paths-file"""
    runner = CliRunner()

    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    # Should pass when only using CLI patterns
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(file1), str(file2), "--ignore-paths", "*.log", "--ignore-paths", "*.txt"],
    )
    assert result.exit_code == 0


def test_ignore_paths_only_file_no_cli(tmp_path):
    """Test --ignore-paths-file works without --ignore-paths"""
    runner = CliRunner()

    file1 = tmp_path / "file1.log"
    file1.write_text("/tmp/file\n", encoding="utf-8")

    file2 = tmp_path / "file2.txt"
    file2.write_text("/tmp/file\n", encoding="utf-8")

    ignore_file = tmp_path / "ignore.txt"
    ignore_file.write_text("*.log\n*.txt\n", encoding="utf-8")

    # Should pass when only using file patterns
    result = runner.invoke(
        hooks.detect_absolute_paths,
        [str(file1), str(file2), "--ignore-paths-file", str(ignore_file)],
    )
    assert result.exit_code == 0


def test_file_is_text_with_unknown_extension(tmp_path):
    target = tmp_path / "notes.unknown"
    target.write_text("/tmp/file\n", encoding="utf-8")

    assert hooks.file_is_text(target)


def test_file_contains_absolute_path_skips_non_text(tmp_path, capsys):
    target = tmp_path / "image.png"
    target.write_bytes(b"/tmp/file\n")

    assert not hooks.file_contains_absolute_path(target)

    captured = capsys.readouterr()
    assert captured.out == ""


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
