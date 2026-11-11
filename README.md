# CCBR Tools 🛠️

<!-- README.md is generated from README.qmd. Please edit that file -->

Utilities for CCBR Bioinformatics Software

[![build](https://github.com/CCBR/Tools/actions/workflows/build-python.yml/badge.svg)](https://github.com/CCBR/Tools/actions/workflows/build-python.yml)
[![docs](https://github.com/CCBR/Tools/actions/workflows/docs-quartodoc.yml/badge.svg)](https://ccbr.github.io/Tools)
[![codecov](https://codecov.io/gh/CCBR/Tools/graph/badge.svg?token=O73NOR65B3)](https://codecov.io/gh/CCBR/Tools)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13377166.svg)](https://doi.org/10.5281/zenodo.13377166)

View the website for more detailed documentation:
<https://CCBR.github.io/Tools>

## Installation

On [biowulf](https://hpc.nih.gov/) you can access the latest release of
`ccbr_tools` by loading the ccbrpipeliner module:

```sh
module load ccbrpipeliner
```

Outside of biowulf, you can install the package with pip:

```sh
pip install git+https://github.com/CCBR/Tools
```

Or specify any tagged version or branch:

```sh
pip install git+https://github.com/CCBR/Tools@latest
```

## Basic usage

### CLI

```sh
ccbr_tools --help
```

    Usage: ccbr_tools [OPTIONS] COMMAND [ARGS]...

      Utilities for CCBR Bioinformatics Software

      For more options, run: ccbr_tools [command] --help

      https://ccbr.github.io/Tools/

    Options:
      -v, --version  Show the version and exit.
      -h, --help     Show this message and exit.

    Commands:
      send-email  Send an email (works on biowulf)
      quarto-add  Add a quarto extension
      install     Install a specific version of a CCBR software package,...
      cite        Print the citation in the desired format
      version     Print the version of ccbr_tools

    All installed tools:
      ccbr-hooks
      ccbr_tools
      gb2gtf
      get_hpcname
      hf
      intersect
      jobby
      jobinfo
      module_list
      peek
      spooker

### Pre-commit hooks

Add the hooks to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/CCBR/Tools
  rev: v0.7.0
  hooks:
    - id: detect-absolute-paths
    - id: sync-nextflow-version
```

View the [reference guide on pre-commit hooks](./reference/hooks.qmd)
for more information.

### Python

```python
import ccbr_tools.shell

print(ccbr_tools.shell.shell_run('echo "Hello, world!"'))
```

    Hello, world!

```python
import ccbr_tools.versions

version = ccbr_tools.versions.match_semver("0.2.3")
version.groupdict()
```

    {'major': '0',
     'minor': '2',
     'patch': '3',
     'prerelease': None,
     'buildmetadata': None}

View the [API reference](https://ccbr.github.io/Tools/reference/) for
more information.

### Running Nextflow workflows

Use `ccbr_tools.pipeline.nextflow.run()` for local execution or SLURM
driver submission. Existing calls still preview automatically and resume
by default. Arguments are a sequence of tokens, not a shell command
string: repeated options, spaces, negative values, and quoted tool
arguments retain their boundaries.

```python
from ccbr_tools.pipeline.nextflow import run

run(
    nextfile_path="/path/to/main.nf",
    cwd="analysis",
    mode="slurm",
    pipeline_name="RENEE",
    nextflow_args=["-c", "one.config", "-c", "two.config", "--threads", "4"],
    preview=False,
    wait=True,
    hpc_partition="student",
    hpc_walltime="12:00:00",
    hpc_memory="4G",
    env={"SINGULARITY_CACHEDIR": "/path/to/private-cache"},
)
```

Create the launch directory first. `cwd` does not change the caller’s
working directory; resolve workflow and argument paths before calling if
they are relative to a different directory. `env` overrides cluster
defaults for previews, local runs, and SLURM scripts without modifying
the parent environment. Callers remain responsible for validating cache
ownership and other application-specific policies.

`preview=False` disables the automatic preflight preview; an explicit
`-preview` always runs locally without submitting a job, even in SLURM
mode. `debug=True` prints commands and writes any submission script
without launching processes. Generic SLURM clusters are supported
without a recognized cluster profile. Module loading and cluster
environment defaults apply only on recognized clusters; use
`hpc_modules=""` to disable module loading there. SLURM logs go to
`log/slurm_%j.log`.

The runner adds `-resume` unless a session is supplied
(`-resume SESSION` or `-resume=SESSION`). `force_all=True` removes
either form. Profiles from repeated `-profile` or `-profile=...` options
are merged with the cluster and execution-mode profiles. Malformed
profile lists raise `ValueError`.

Preview, workflow, and submission failures raise
`subprocess.CalledProcessError`. With `wait=True`, `sbatch --wait` also
reports driver job failure; without it, successful submission does not
imply workflow completion. Module and environment setup failures stop
execution instead of being hidden by a later command.

## CLI Utilities

Command-line utilities in CCBR Tools.

- `ccbr-hooks`
- `ccbr_tools`
- `gb2gtf`
- `get_hpcname`
- `hf`
- `intersect`
- `jobby`
- `jobinfo`
- `module_list`
- `peek`
- `spooker`

Run a command with `--help` to learn how to use it.

## External Scripts

Additional standalone scripts for various common tasks in
[scripts/](scripts/) are added to the path when this package is
installed. They are less robust than the CLI Utilities included in the
package and do not have any unit tests.

- [`add_gene_name_to_count_matrix.R`](scripts/add_gene_name_to_count_matrix.R)
- [`aggregate_data_tables.R`](scripts/aggregate_data_tables.R)
- [`argparse.bash`](scripts/argparse.bash)
- [`cancel_snakemake_jobs.sh`](scripts/cancel_snakemake_jobs.sh)
- [`extract_value_from_json.py`](scripts/extract_value_from_json.py)
- [`extract_value_from_yaml.py`](scripts/extract_value_from_yaml.py)
- [`filter_bam_by_readids.py`](scripts/filter_bam_by_readids.py)
- [`filter_fastq_by_readids_highmem.py`](scripts/filter_fastq_by_readids_highmem.py)
- [`filter_fastq_by_readids_highmem_pe.py`](scripts/filter_fastq_by_readids_highmem_pe.py)
- [`gather_cluster_stats.sh`](scripts/gather_cluster_stats.sh)
- [`gather_cluster_stats_biowulf.sh`](scripts/gather_cluster_stats_biowulf.sh)
- [`get_buyin_partition_list.bash`](scripts/get_buyin_partition_list.bash)
- [`get_slurm_file_with_error.sh`](scripts/get_slurm_file_with_error.sh)
- [`github_milestones.sh`](scripts/github_milestones.sh)
- [`gsea_preranked.sh`](scripts/gsea_preranked.sh)
- [`karyoploter.R`](scripts/karyoploter.R)
- [`make_labels_for_pipeliner.sh`](scripts/make_labels_for_pipeliner.sh)
- [`rawcounts2normalizedcounts_DESeq2.R`](scripts/rawcounts2normalizedcounts_DESeq2.R)
- [`rawcounts2normalizedcounts_limmavoom.R`](scripts/rawcounts2normalizedcounts_limmavoom.R)
- [`run_jobby_on_nextflow_log`](scripts/run_jobby_on_nextflow_log)
- [`run_jobby_on_nextflow_log_full_format`](scripts/run_jobby_on_nextflow_log_full_format)
- [`run_jobby_on_snakemake_log`](scripts/run_jobby_on_snakemake_log)
- [`run_jobby_on_snakemake_log_full_format`](scripts/run_jobby_on_snakemake_log_full_format)
- [`which_vpn.sh`](scripts/which_vpn.sh)

## Help & Contributing

Come across a **bug**? Open an
[issue](https://github.com/CCBR/Tools/issues) and include a minimal
reproducible example.

Have a **question**? Ask it in
[discussions](https://github.com/CCBR/Tools/discussions).

Want to **contribute** to this project? Check out the [contributing
guidelines](https://CCBR.github.io/Tools/CONTRIBUTING).

## Citation

Please cite this software if you use it in a publication:

> Sovacool K., Koparde V., Kuhn S., Tandon M., and Huse S. (2026). CCBR
> Tools: Utilities for CCBR Bioinformatics Software (version v0.7.1).
> DOI: 10.5281/zenodo.13377166 URL: https://ccbr.github.io/Tools/

### Bibtex entry

```bibtex
@misc{YourReferenceHere,
author = {Sovacool, Kelly and Koparde, Vishal and Kuhn, Skyler and Tandon, Mayank and Huse, Susan},
doi = {10.5281/zenodo.13377166},
month = {9},
title = {CCBR Tools: Utilities for CCBR Bioinformatics Software},
url = {https://ccbr.github.io/Tools/},
year = {2026}
}
```
