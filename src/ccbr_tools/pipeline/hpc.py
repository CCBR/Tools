from .util import get_hpcname
from .cache import get_singularity_cachedir


class Cluster:
    def __init__(self):
        self.name = None
        self.modules = {"nxf": None, "smk": None}
        self.env_vars = "\n".join(
            (f"export SINGULARITY_CACHEDIR={get_singularity_cachedir()}",)
        )
        self.singularity_sif_dir = None

    def __repr__(self):
        return f"{self.__class__}({self.__dict__})"

    def __bool__(self):
        return bool(self.name)

    __nonzero__ = __bool__


class Biowulf(Cluster):
    def __init__(self):
        super().__init__()
        self.name = "biowulf"
        self.modules = {
            "nxf": "ccbrpipeliner nextflow",
            "smk": "ccbrpipeliner snakemake/7 singularity",
        }
        self.singularity_sif_dir = "/data/CCBR_Pipeliner/SIFs"


class FRCE(Cluster):
    def __init__(self):
        super().__init__()
        self.name = "frce"
        self.modules = {"nxf": "nextflow", "smk": "snakemake/7 singularity"}
        self.singularity_sif_dir = "/mnt/projects/CCBR-Pipelines/SIFs"
        self.env_vars = "\n".join(
            (
                self.env_vars,
                "export PATH=${PATH}:/mnt/projects/CCBR-Pipelines/bin",
            )
        )


def get_hpc(debug=False):
    hpc_options = {"biowulf": Biowulf, "frce": FRCE}
    hpc_name = get_hpcname() if not debug else debug
    return hpc_options.get(hpc_name, Cluster)()
