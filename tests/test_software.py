from ccbr_tools.software import Software
from ccbr_tools.pipeline.hpc import Biowulf


def test_python():
    assert all(
        [
            Software.create_software("ccbr_tools", "v0.3.2").url
            == "https://github.com/CCBR/tools.git",
            Software.create_software("ccbr_actions", "v0.1.2").url
            == "https://github.com/CCBR/actions.git",
            Software.create_software("ccbr_actions", "v1.0.0-dev").install(
                hpc=Biowulf, branch_tag="main"
            )
            == "pip install git+https://github.com/CCBR/actions.git@main -t /data/CCBR_Pipeliner/Tools/ccbr_actions/.v1.0.0-dev",
        ]
    )


def test_pipelines():
    assert all(
        [
            Software.create_software("CHAMPAGNE", "v0.3.0").install(hpc=Biowulf)
            == "pip install git+https://github.com/CCBR/CHAMPAGNE.git@v0.3.0 -t /data/CCBR_Pipeliner/Pipelines/CHAMPAGNE/.v0.3.0",
            Software.create_software("XAVIER", "v3.0.1").install(hpc=Biowulf)
            == "git clone --depth 1 --single-branch --branch v3.0.1 https://github.com/CCBR/XAVIER.git /data/CCBR_Pipeliner/Pipelines/XAVIER/.v3.0.1",
        ]
    )


def test_bash():
    assert (
        Software.create_software("permfix", "v1.2.3").install(Biowulf)
        == "git clone --depth 1 --single-branch --branch v1.2.3 https://github.com/CCBR/permfix.git /data/CCBR_Pipeliner/Tools/permfix/.v1.2.3"
    )
