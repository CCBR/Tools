from .util import get_hpcname


class Cluster:
    def __init__(self):
        self.name = None
        self.slurm_script = {"nxf": None, "smk": None}
        self.modules = {"nxf": None, "smk": None}
        self.singularity_sif_dir = None

    def __bool__(self):
        return bool(self.name)

    __nonzero__ = __bool__


class Biowulf(Cluster):
    def __init__(self):
        super().__init__()
        self.name = "biowulf"
        self.slurm_script = {
            "nxf": "slurm_nxf_biowulf.sh",
            "smk": "slurm_smk_biowulf.sh",
        }
        self.modules = {
            "nxf": "ccbrpipeliner nextflow",
            "smk": "ccbrpipeliner snakemake/7 singularity",
        }
        self.singularity_sif_dir = "/data/CCBR_Pipeliner/SIFs"


class FRCE(Cluster):
    def __init__(self):
        super().__init__()
        self.name = "frce"
        self.slurm_script = {"nxf": "slurm_nxf_frce.sh", "smk": "slurm_smk_frce.sh"}
        self.modules = {"nxf": "nextflow", "smk": "snakemake/7 singularity"}
        self.singularity_sif_dir = "/mnt/projects/CCBR-Pipelines/SIFs"


def get_hpc(debug=False):
    hpc_options = {"biowulf": Biowulf, "frce": FRCE}
    hpc_name = get_hpcname() if not debug else debug
    return hpc_options.get(hpc_name, Cluster)()
