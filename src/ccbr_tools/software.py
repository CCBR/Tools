from .pipeline.hpc import Cluster
from .shell import shell_run
from .versions import match_semver, get_major_minor_version


class Software:
    @staticmethod
    def create_software(tool_name, version, software_type=None):
        tool_lower = tool_name.lower()

        if software_type:
            software = eval(software_type)(tool_name, version)
        else:
            if tool_lower not in CCBR_SOFTWARE:
                raise KeyError(
                    f"{tool_name} not found in software list.\t\n{', '.join(CCBR_SOFTWARE.keys())}"
                )
            software = CCBR_SOFTWARE[tool_lower](tool_name, version)
        return software

    def __init__(self, name, version):
        self.name = name
        self.version = version
        assert (
            self.version_re
        ), f"Invalid version format '{version}' - Must be a valid semantic version."

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.version})"

    def path(self, hpc: Cluster):
        hidden_dir = self.hidden_version
        return hpc.TOOLS_HOME / self.name / hidden_dir

    def base_path(self, hpc: Cluster):
        return hpc.TOOLS_HOME / self.name

    @property
    def version_re(self):
        return match_semver(self.version, with_leading_v=True)

    @property
    def major_minor(self):
        version_mm = get_major_minor_version(self.version, with_leading_v=True)
        assert version_mm
        return version_mm

    @property
    def hidden_version(self):
        return f".{self.version}"

    @property
    def is_dev_version(self):
        return self.version_re.group("prerelease") or self.version_re.group(
            "buildmetadata"
        )

    @property
    def url(self):
        return f"https://github.com/CCBR/{self.name}.git"

    def install(self, hpc: Cluster, branch_tag=None):
        raise NotImplementedError("Subclasses should implement this method")


class Installer:
    @staticmethod
    def python(software: Software, hpc: Cluster, branch_tag=None):
        tag = software.version if not branch_tag else branch_tag
        return f"pip install git+{software.url}@{tag} -t {software.path(hpc)}"

    @staticmethod
    def bash(software: Software, hpc: Cluster, branch_tag=None):
        tag = software.version if not branch_tag else branch_tag
        return f"git clone --depth 1 --single-branch --branch {tag} {software.url} {software.path(hpc)}"


class PythonTool(Software):
    def __init__(self, name, version):
        super(PythonTool, self).__init__(name, version)
        self.repo_name = name.replace("ccbr_", "")

    def install(self, hpc: Cluster, branch_tag=None):
        return Installer.python(self, hpc, branch_tag=branch_tag)

    @property
    def url(self):
        return f"https://github.com/CCBR/{self.repo_name}.git"


class BashTool(Software):
    def __init__(self, name, version):
        super(BashTool, self).__init__(name, version)

    def install(self, hpc: Cluster, branch_tag=None):
        return Installer.bash(self, hpc, branch_tag=branch_tag)


class Nextflow(Software):
    def __init__(self, name, version):
        super(Nextflow, self).__init__(name.upper(), version)

    def path(self, hpc: Cluster):
        hidden_dir = self.hidden_version
        return hpc.PIPELINES_HOME / self.name / hidden_dir

    def base_path(self, hpc: Cluster):
        return hpc.PIPELINES_HOME / self.name

    def install(self, hpc: Cluster, branch_tag=None):
        return Installer.python(self, hpc, branch_tag=branch_tag)


class Snakemake(Software):
    def __init__(self, name, version):
        super(Snakemake, self).__init__(name.upper(), version)

    def path(self, hpc: Cluster):
        hidden_dir = self.hidden_version
        return hpc.PIPELINES_HOME / self.name / hidden_dir

    def base_path(self, hpc: Cluster):
        return hpc.PIPELINES_HOME / self.name

    def install(self, hpc: Cluster, branch_tag=None):
        return Installer.bash(self, hpc, branch_tag=branch_tag)


CCBR_SOFTWARE = {
    "aspen": Snakemake,
    "carlisle": Snakemake,
    "champagne": Nextflow,
    "charlie": Snakemake,
    "crispin": Nextflow,
    "escape": Snakemake,
    "logan": Nextflow,
    "renee": Snakemake,
    "sinclair": Nextflow,
    "xavier": Snakemake,
    "spacesavers2": PythonTool,
    "permfix": BashTool,
    "ccbr_tools": PythonTool,
    "ccbr_actions": PythonTool,
}


SET_SYMLINK = """
pushd {BASE_PATH}
rm -if {MAJOR_MINOR_VERSION}
ln -s {HIDDEN_VERSION} {MAJOR_MINOR_VERSION}
popd"""

INSTALL_SCRIPT = """{CONDA_ACTIVATE}
{INSTALL}
chmod -R a+rX {PATH}
chown -R :{GROUP} {PATH}"""


def install(
    tool_name,
    version,
    dryrun=True,
    branch_tag=None,
    software_type=None,
    install_script=INSTALL_SCRIPT,
    symlink_script=SET_SYMLINK,
    debug=False,
):
    hpc = Cluster.create_hpc(debug=debug)
    tool = Software.create_software(tool_name, version, software_type=software_type)

    script = install_script.format(
        GROUP=hpc.GROUP,
        CONDA_ACTIVATE=hpc.CONDA_ACTIVATE,
        INSTALL=tool.install(hpc, branch_tag=branch_tag),
        PATH=tool.path(hpc),
    )
    if not tool.is_dev_version:
        script += symlink_script.format(
            BASE_PATH=tool.base_path(hpc),
            HIDDEN_VERSION=tool.hidden_version,
            MAJOR_MINOR_VERSION=tool.major_minor,
        )
    if dryrun:
        print(script)
    else:
        shell_run(script, shell=True, capture_output=False)
