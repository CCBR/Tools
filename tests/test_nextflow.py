import json
import os
import pathlib
import subprocess
from unittest.mock import Mock

import pytest

from ccbr_tools.pipeline.hpc import FRCE, Biowulf, Cluster
from ccbr_tools.pipeline.nextflow import init, run
from ccbr_tools.shell import exec_in_context


def test_init(tmp_path, data_dir):
    """Test init."""
    init(
        output=tmp_path,
        repo_base=lambda f: data_dir / "pipeline" / f,
        pipeline_name="test_pipeline",
    )
    assert (tmp_path / "log").exists()
    assert (tmp_path / "nextflow.config").exists()
    assert (tmp_path / "conf").exists()
    assert (tmp_path / "assets").exists()


def test_nextflow_basic():
    """Test nextflow basic."""
    output = exec_in_context(run, nextfile_path="CCBR/CHAMPAGNE", debug=True)
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" in output


def test_nextflow_forceall():
    """Test nextflow forceall."""
    output = exec_in_context(
        run, nextfile_path="CCBR/CHAMPAGNE", debug=True, force_all=True
    )
    assert "nextflow run CCBR/CHAMPAGNE" in output and "-resume" not in output


@pytest.mark.parametrize(
    "hpc, modules", [(Biowulf(), "nextflow/25"), (FRCE(), "nextflow")]
)
def test_nextflow_hpc(hpc, modules, monkeypatch):
    """Test nextflow hpc."""
    process = Mock()
    monkeypatch.setattr("ccbr_tools.pipeline.nextflow.subprocess.run", process)
    run("CCBR/CHAMPAGNE", hpc=hpc, hpc_modules=modules, preview=False)
    script = process.call_args.args[0][2]
    assert f"module load {modules}\n" in script
    assert hpc.env_vars in script
    assert f"-profile {hpc.name}" in script


def test_nextflow_slurm(tmp_path):
    """Test nextflow slurm."""
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        out = exec_in_context(
            run, nextfile_path="CCBR/CHAMPAGNE", debug=True, hpc=Biowulf(), mode="slurm"
        )
        slurm_txt = (tmp_path / "submit_slurm.sh").read_text()
    finally:
        os.chdir(current_wd)
    assert "sbatch submit_slurm.sh" in out
    assert "nextflow run CCBR/CHAMPAGNE" in slurm_txt
    assert "modules=(nextflow)" in slurm_txt
    assert '#SBATCH -J "CCBR/CHAMPAGNE"' in slurm_txt


def test_nextflow_preview_error(tmp_path, data_dir_rel, monkeypatch):
    """Test nextflow preview error."""
    executable = tmp_path / "nextflow"
    executable.write_text("#!/usr/bin/env bash\nexit 1\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    current_wd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        with pytest.raises(subprocess.CalledProcessError) as err:
            exec_in_context(
                run,
                nextfile_path=str(data_dir_rel / "nextflow" / "main.nf"),
                debug=False,
                mode="local",
                hpc=Cluster(),
            )
    finally:
        os.chdir(current_wd)
    assert err.value.returncode == 1
    assert (
        f"nextflow run {data_dir_rel / 'nextflow' / 'main.nf'} -resume -preview"
        in err.value.cmd[2]
    )


def test_argument_boundaries_and_environment(tmp_path, monkeypatch):
    """Run a fake binary to verify argv, cwd, and environment in both launches."""
    executable = tmp_path / "nextflow"
    executable.write_text(
        "#!/usr/bin/env python\nimport json, os, sys\n"
        "with open('calls.jsonl', 'a') as out:\n"
        "    out.write(json.dumps([sys.argv[1:], os.environ['CACHE']]) + '\\n')\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CACHE", "parent")
    current_wd = pathlib.Path.cwd()
    args = [
        "-c",
        "one config",
        "-c",
        "two config",
        "--value",
        "--foo bar",
        "--negative",
        "-1",
        "--literal=$(touch unwanted)",
        "--empty",
        "",
        "-profile=singularity",
        "-profile",
        "test",
        "-resume",
        "session",
    ]
    run(
        "main file.nf",
        cwd=tmp_path,
        hpc=Cluster(),
        nextflow_args=args,
        env={"CACHE": "private cache; $HOME"},
    )
    calls = [
        json.loads(line) for line in (tmp_path / "calls.jsonl").read_text().splitlines()
    ]
    expected = [
        "run",
        "main file.nf",
        *args[:-5],
        "-resume",
        "session",
        "-profile",
        "singularity,test",
    ]
    assert calls == [
        [expected + ["-preview"], "private cache; $HOME"],
        [expected, "private cache; $HOME"],
    ]
    assert not (tmp_path / "unwanted").exists()
    assert pathlib.Path.cwd() == current_wd
    assert os.environ["CACHE"] == "parent"


@pytest.mark.parametrize(
    "resume", [[], ["-resume"], ["-resume", "old"], ["-resume=old"]]
)
def test_force_all_resume_forms(resume):
    """Remove explicit resume sessions while leaving unrelated arguments intact."""
    out = exec_in_context(
        run,
        "main.nf",
        hpc=Cluster(),
        debug=True,
        force_all=True,
        nextflow_args=[*resume, "--value", "kept"],
    )
    assert "-resume" not in out
    assert "--value kept" in out


@pytest.mark.parametrize(
    "args", [["-profile"], ["-profile="], ["-profile", "-preview"], ["-profile=a,"]]
)
def test_invalid_profiles(args):
    """Reject malformed profiles rather than consuming another option."""
    with pytest.raises(ValueError, match="-profile requires"):
        run("main.nf", hpc=Cluster(), nextflow_args=args, debug=True)


def test_slurm_options_and_explicit_preview(tmp_path, monkeypatch):
    """Generic clusters support submission controls; explicit previews stay local."""
    process = Mock()
    monkeypatch.setattr("ccbr_tools.pipeline.nextflow.subprocess.run", process)
    run(
        "main.nf",
        cwd=tmp_path,
        mode="slurm",
        hpc=Cluster(),
        preview=False,
        wait=True,
        hpc_partition="student",
        hpc_walltime="12:00:00",
        hpc_memory="4G",
        pipeline_name="RENEE",
        env={"CACHE": "private cache"},
    )
    process.assert_called_once_with(
        ["sbatch", "--wait", "--partition=student", "submit_slurm.sh"],
        cwd=tmp_path,
        check=True,
    )
    script = (tmp_path / "submit_slurm.sh").read_text()
    assert "#SBATCH --time=12:00:00" in script
    assert "#SBATCH --mem=4G" in script
    assert "export CACHE='private cache'" in script
    assert "modules=()" in script
    assert "-profile slurm" in script
    process.reset_mock()
    run(
        "main.nf", cwd=tmp_path, mode="slurm", hpc=Cluster(), nextflow_args=["-preview"]
    )
    process.assert_called_once()
    assert process.call_args.args[0][:2] == ["bash", "-c"]


@pytest.mark.parametrize("preview", [True, False])
@pytest.mark.parametrize("mode", ["local", "slurm"])
def test_failures_propagate(tmp_path, monkeypatch, preview, mode):
    """Never return success after a failed preview, workflow, or submission."""
    process = Mock(side_effect=subprocess.CalledProcessError(9, "failed"))
    monkeypatch.setattr("ccbr_tools.pipeline.nextflow.subprocess.run", process)
    with pytest.raises(subprocess.CalledProcessError):
        run("main.nf", cwd=tmp_path, hpc=Cluster(), preview=preview, mode=mode)
    process.assert_called_once()


def test_invalid_mode_and_environment(tmp_path):
    """Validate inputs before writing a script or launching processes."""
    with pytest.raises(ValueError, match="mode invalid"):
        run("main.nf", mode="invalid", cwd=tmp_path)
    with pytest.raises(ValueError, match="Invalid environment variable"):
        run("main.nf", hpc=Cluster(), env={"INVALID;": "value"}, cwd=tmp_path)
    assert not (tmp_path / "submit_slurm.sh").exists()


def test_slurm_script_execution(tmp_path, monkeypatch):
    """Execute the generated driver through a fake sbatch, including job failure."""
    nextflow = tmp_path / "nextflow"
    nextflow.write_text(
        "#!/usr/bin/env python\nimport json, os, sys\n"
        "from pathlib import Path\n"
        "Path('driver.json').write_text(json.dumps([sys.argv[1:], os.environ['CACHE']]))\n"
        "sys.exit(9 if '--fail' in sys.argv else 0)\n"
    )
    sbatch = tmp_path / "sbatch"
    sbatch.write_text(
        '#!/usr/bin/env bash\nfor arg; do script="$arg"; done\nexec bash "$script"\n'
    )
    for executable in [nextflow, sbatch]:
        executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    run(
        "main file.nf",
        cwd=tmp_path,
        mode="slurm",
        hpc=Cluster(),
        preview=False,
        wait=True,
        nextflow_args=["--value", "--foo bar"],
        env={"CACHE": "cache with spaces; $HOME"},
    )
    assert json.loads((tmp_path / "driver.json").read_text()) == [
        ["run", "main file.nf", "--value", "--foo bar", "-resume", "-profile", "slurm"],
        "cache with spaces; $HOME",
    ]
    with pytest.raises(subprocess.CalledProcessError) as error:
        run(
            "main.nf",
            cwd=tmp_path,
            mode="slurm",
            hpc=Cluster(),
            preview=False,
            wait=True,
            nextflow_args=["--fail"],
            env={"CACHE": "test"},
        )
    assert error.value.returncode == 9


def test_setup_failure_stops_execution(tmp_path):
    """Cluster setup errors must not be hidden by a successful workflow command."""
    hpc = Cluster()
    hpc.name = "test"
    hpc.env_vars = "false"
    with pytest.raises(subprocess.CalledProcessError) as error:
        run("main.nf", cwd=tmp_path, hpc=hpc, hpc_modules="", preview=False)
    assert error.value.returncode == 1


if __name__ == "__main__":
    test_nextflow_slurm()
