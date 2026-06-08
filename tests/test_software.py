from ccbr_tools.software import (
    Software,
    install,
    SET_SYMLINK,
    LATEST_SYMLINK,
    FINAL_PERMISSIONS,
)
from ccbr_tools.pipeline.hpc import Biowulf
from ccbr_tools.shell import exec_in_context

import pytest


def test_python():
    assert (
        Software.create_software("ccbr_tools", "v0.3.2").url
        == "https://github.com/CCBR/tools.git"
    )
    assert (
        Software.create_software("ccbr_actions", "v0.1.2").url
        == "https://github.com/CCBR/actions.git"
    )
    assert (
        Software.create_software("ccbr_actions", "v1.0.0-dev").install(
            hpc=Biowulf, branch_tag="main"
        )
        == "pip install git+https://github.com/CCBR/actions.git@main -t /data/CCBR_Pipeliner/Tools/ccbr_actions/.v1.0.0-dev"
    )


def test_pipelines():
    assert (
        Software.create_software("CHAMPAGNE", "v0.3.0").install(hpc=Biowulf)
        == "pip install git+https://github.com/CCBR/CHAMPAGNE.git@v0.3.0 -t /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0"
    )
    assert (
        Software.create_software("XAVIER", "v3.0.1").install(hpc=Biowulf)
        == "git clone --depth 1 --single-branch --branch v3.0.1 https://github.com/CCBR/XAVIER.git /data/CCBR_Pipeliner/Pipelines/XAVIER/.v3.0.1"
    )


def test_bash():
    assert (
        Software.create_software("permfix", "v1.2.3").install(Biowulf)
        == "git clone --depth 1 --single-branch --branch v1.2.3 https://github.com/CCBR/permfix.git /data/CCBR_Pipeliner/Tools/permfix/.v1.2.3"
    )


def test_install():
    result = exec_in_context(
        install, tool_name="CHAMPAGNE", version="v0.3.0", dryrun=True, debug="biowulf"
    )
    assert "mamba activate /" in result
    assert (
        """pip install git+https://github.com/CCBR/CHAMPAGNE.git@v0.3.0 -t /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0
pushd /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE
rm -f v0.3
ln -s .v0.3.0 v0.3
popd
pushd /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE
rm -f latest
ln -s v0.3 latest
popd
chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE
chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE
"""
        in result
    )


def test_install_dev():
    result = exec_in_context(
        install,
        tool_name="CHAMPAGNE",
        version="v0.3.0-dev",
        branch_tag="main",
        dryrun=True,
        debug="biowulf",
    )
    assert "mamba activate /" in result
    assert (
        "pip install git+https://github.com/CCBR/CHAMPAGNE.git@main -t /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0-dev"
        in result
    )
    assert "latest" not in result
    assert "chmod" not in result
    assert "chown" not in result


def test_custom():
    result = exec_in_context(
        install,
        tool_name="cooltool",
        version="v1.0.0",
        dryrun=True,
        software_type="PythonTool",
        debug="biowulf",
    )
    assert "mamba activate /" in result
    assert (
        """pip install git+https://github.com/CCBR/cooltool.git@v1.0.0 -t /data/CCBR_Pipeliner/Tools/cooltool/.v1.0.0
pushd /data/CCBR_Pipeliner/Tools/cooltool
rm -f v1.0
ln -s .v1.0.0 v1.0
popd
pushd /data/CCBR_Pipeliner/Tools/cooltool
rm -f latest
ln -s v1.0 latest
popd
chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Tools/cooltool
chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Tools/cooltool
"""
        in result
    )


def test_unsupported():
    with pytest.raises(KeyError) as exc_info:
        Software.create_software("unsupported_tool", "v1.0.0")
        assert str(exc_info.value).startswith(
            "unsupported_tool not found in software list"
        )


class TestSymlinkTemplates:
    """Tests for symlink and permission templates."""

    def test_set_symlink_template(self):
        """Verify SET_SYMLINK template creates major.minor symlink with rm -f."""
        script = SET_SYMLINK.format(
            BASE_PATH="/data/test",
            HIDDEN_VERSION=".v2.7.6",
            MAJOR_MINOR_VERSION="v2.7",
        )
        assert "rm -f v2.7" in script
        assert "ln -s .v2.7.6 v2.7" in script
        assert "pushd /data/test" in script
        assert "popd" in script
        assert "chmod" not in script

    def test_latest_symlink_template(self):
        """Verify LATEST_SYMLINK template creates latest symlink with rm -f."""
        script = LATEST_SYMLINK.format(
            BASE_PATH="/data/test",
            MAJOR_MINOR_VERSION="v2.7",
        )
        assert "rm -f latest" in script
        assert "ln -s v2.7 latest" in script
        assert "pushd /data/test" in script
        assert "popd" in script

    def test_final_permissions_template(self):
        """Verify FINAL_PERMISSIONS applies correct chmod and chown."""
        script = FINAL_PERMISSIONS.format(
            GROUP="CCBR_Pipeliner",
            BASE_PATH="/data/CCBR_Pipeliner/Pipelines/RENEE",
        )
        assert "chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Pipelines/RENEE" in script
        assert "chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Pipelines/RENEE" in script

    def test_final_permissions_flags(self):
        """Verify FINAL_PERMISSIONS uses correct permission flags."""
        assert "u-w" in FINAL_PERMISSIONS
        assert "g-w" in FINAL_PERMISSIONS
        assert "o-w" in FINAL_PERMISSIONS
        assert "a+rX" in FINAL_PERMISSIONS
        assert "a+rx" not in FINAL_PERMISSIONS


class TestInstallSymlinkChain:
    """Tests for the complete symlink chain creation."""

    def test_install_creates_major_minor_symlink(self):
        """Verify install creates major.minor version symlink."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "rm -f v2.7" in result
        assert "ln -s .v2.7.6 v2.7" in result

    def test_install_creates_latest_symlink(self):
        """Verify install creates latest symlink pointing to major.minor."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "rm -f latest" in result
        assert "ln -s v2.7 latest" in result

    def test_install_applies_final_permissions(self):
        """Verify install applies final permissions recursively."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Pipelines/RENEE" in result
        assert (
            "chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Pipelines/RENEE"
            in result
        )

    def test_install_symlink_order(self):
        """Verify symlinks are created in correct order."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        major_minor_pos = result.find("ln -s .v2.7.6 v2.7")
        latest_pos = result.find("ln -s v2.7 latest")
        perms_pos = result.find("chmod -R u-w,g-w,o-w,a+rX")

        assert (
            major_minor_pos < latest_pos < perms_pos
        ), "Symlinks must be created before permissions are applied"

    def test_install_no_intermediate_permissions(self):
        """Verify install does not apply intermediate permissions."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "chmod -R a+rX" not in result
        assert "chmod -R g+rwX" not in result
        lines = result.split("\n")
        chmod_lines = [line for line in lines if "chmod -R u-w,g-w,o-w,a+rX" in line]
        assert len(chmod_lines) == 1, "Should have exactly one chmod command"

    def test_dev_version_no_symlinks(self):
        """Verify dev versions do not create symlinks or permissions."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.0-dev",
            dryrun=True,
            debug="biowulf",
        )
        assert "rm -f latest" not in result
        assert "ln -s" not in result
        assert "chmod" not in result
        assert "chown" not in result


class TestRENEEPipelineInstall:
    """Integration tests for RENEE pipeline installation."""

    def test_renee_snakemake_path(self):
        """Verify RENEE uses correct pipeline path."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "/data/CCBR_Pipeliner/Pipelines/RENEE" in result

    def test_renee_uses_git_clone(self):
        """Verify RENEE (Snakemake) uses git clone for installation."""
        result = exec_in_context(
            install,
            tool_name="RENEE",
            version="v2.7.6",
            dryrun=True,
            debug="biowulf",
        )
        assert "git clone --depth 1" in result
        assert "https://github.com/CCBR/RENEE.git" in result


class TestBashToolInstall:
    """Integration tests for BashTool installation (e.g., permfix)."""

    def test_bashtool_latest_symlink(self):
        """Verify BashTool also creates latest symlink."""
        result = exec_in_context(
            install,
            tool_name="permfix",
            version="v1.2.3",
            dryrun=True,
            debug="biowulf",
        )
        assert "rm -f latest" in result
        assert "ln -s v1.2 latest" in result

    def test_bashtool_final_permissions(self):
        """Verify BashTool applies final permissions."""
        result = exec_in_context(
            install,
            tool_name="permfix",
            version="v1.2.3",
            dryrun=True,
            debug="biowulf",
        )
        assert (
            "chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Tools/permfix"
            in result
        )
