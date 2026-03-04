from click.testing import CliRunner

import ccbr_tools.__main__ as main_mod


def test_cli_version_command(mocker):
    runner = CliRunner()
    mock_get_version = mocker.patch.object(
        main_mod, "get_version", return_value="1.2.3"
    )

    result = runner.invoke(main_mod.cli, ["version"])

    assert result.exit_code == 0
    assert result.output == "1.2.3\n"
    mock_get_version.assert_called_once()


def test_cli_cite_command(mocker, tmp_path):
    runner = CliRunner()
    citation_file = tmp_path / "CITATION.cff"
    citation_file.write_text("cff-version: 1.2.0\nmessage: test\n", encoding="utf-8")

    mock_print_citation = mocker.patch.object(main_mod, "print_citation")

    result = runner.invoke(main_mod.cli, ["cite", str(citation_file), "-f", "bibtex"])

    assert result.exit_code == 0
    mock_print_citation.assert_called_once_with(
        citation_file=str(citation_file), output_format="bibtex"
    )


def test_cli_send_email_command(mocker):
    runner = CliRunner()
    mock_send_email = mocker.patch.object(main_mod, "send_email_msg")

    result = runner.invoke(
        main_mod.cli,
        [
            "send-email",
            "to@example.com",
            "hello",
            "-s",
            "Subject",
            "-r",
            "from@example.com",
            "-d",
        ],
    )

    assert result.exit_code == 0
    mock_send_email.assert_called_once_with(
        "to@example.com", "hello", "Subject", None, "from@example.com", True
    )


def test_cli_quarto_add_command(mocker):
    runner = CliRunner()
    mock_use_quarto_ext = mocker.patch.object(main_mod, "use_quarto_ext")

    result = runner.invoke(main_mod.cli, ["quarto-add", "fnl"])

    assert result.exit_code == 0
    mock_use_quarto_ext.assert_called_once_with("fnl")


def test_cli_install_command(mocker):
    runner = CliRunner()
    mock_install = mocker.patch.object(main_mod, "install_software")

    result = runner.invoke(
        main_mod.cli,
        [
            "install",
            "demo",
            "v1.2.3",
            "--run",
            "--branch",
            "dev",
            "--type",
            "custom",
            "--hpc",
            "biowulf",
        ],
    )

    assert result.exit_code == 0
    mock_install.assert_called_once_with(
        "demo",
        "v1.2.3",
        dryrun=False,
        branch_tag="dev",
        software_type="custom",
        debug="biowulf",
    )
