from click.testing import CliRunner

import ccbr_tools.__main__ as main_mod


def test_cli_version_command(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(main_mod, "get_version", lambda debug=False: "1.2.3")

    result = runner.invoke(main_mod.cli, ["version"])

    assert result.exit_code == 0
    assert result.output == "1.2.3\n"


def test_cli_cite_command(monkeypatch, tmp_path):
    runner = CliRunner()
    citation_file = tmp_path / "CITATION.cff"
    citation_file.write_text("cff-version: 1.2.0\nmessage: test\n", encoding="utf-8")

    captured = {}

    def fake_print_citation(citation_file, output_format):
        captured["citation_file"] = citation_file
        captured["output_format"] = output_format

    monkeypatch.setattr(main_mod, "print_citation", fake_print_citation)

    result = runner.invoke(main_mod.cli, ["cite", str(citation_file), "-f", "bibtex"])

    assert result.exit_code == 0
    assert captured["citation_file"] == str(citation_file)
    assert captured["output_format"] == "bibtex"


def test_cli_send_email_command(monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_send_email(to_addr, text, subject, attach_html, from_addr, debug):
        captured["to_addr"] = to_addr
        captured["text"] = text
        captured["subject"] = subject
        captured["attach_html"] = attach_html
        captured["from_addr"] = from_addr
        captured["debug"] = debug

    monkeypatch.setattr(main_mod, "send_email_msg", fake_send_email)

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
    assert captured["to_addr"] == "to@example.com"
    assert captured["text"] == "hello"
    assert captured["subject"] == "Subject"
    assert captured["from_addr"] == "from@example.com"
    assert captured["debug"] is True


def test_cli_quarto_add_command(monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_use_quarto_ext(ext_name):
        captured["ext_name"] = ext_name

    monkeypatch.setattr(main_mod, "use_quarto_ext", fake_use_quarto_ext)

    result = runner.invoke(main_mod.cli, ["quarto-add", "fnl"])

    assert result.exit_code == 0
    assert captured["ext_name"] == "fnl"


def test_cli_install_command(monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_install(tool_name, version_tag, dryrun, branch_tag, software_type, debug):
        captured["tool_name"] = tool_name
        captured["version_tag"] = version_tag
        captured["dryrun"] = dryrun
        captured["branch_tag"] = branch_tag
        captured["software_type"] = software_type
        captured["debug"] = debug

    monkeypatch.setattr(main_mod, "install_software", fake_install)

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
    assert captured["tool_name"] == "demo"
    assert captured["version_tag"] == "v1.2.3"
    assert captured["dryrun"] is False
    assert captured["branch_tag"] == "dev"
    assert captured["software_type"] == "custom"
    assert captured["debug"] == "biowulf"
