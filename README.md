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
pip install git+https://github.com/CCBR/Tools@v0.2.4
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
      ccbr_tools
      gb2gtf
      hf
      intersect
      jobby
      jobinfo
      module_list
      peek
      spooker

### Python

```python
import ccbr_tools.shell
print(ccbr_tools.shell.shell_run('echo "Hello, world!"'))
```

    Hello, world!

```python
import ccbr_tools.versions
version = ccbr_tools.versions.match_semver('0.2.3')
version.groupdict()
```

    {'major': '0',
     'minor': '2',
     'patch': '3',
     'prerelease': None,
     'buildmetadata': None}

View the API reference for more information:
<https://ccbr.github.io/Tools/reference/>

## CLI Utilities

Command-line utilities in CCBR Tools.

- `ccbr_tools`
- `gb2gtf`
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
- [`create_hpc_link.sh`](scripts/create_hpc_link.sh)
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

> Sovacool K., Koparde V., Kuhn S., Tandon M., and Huse S. (2025). CCBR
> Tools: Utilities for CCBR Bioinformatics Software (version v0.3.2).
> DOI: 10.5281/zenodo.13377166 URL: https://ccbr.github.io/Tools/

### Bibtex entry

```bibtex
@misc{YourReferenceHere,
author = {Sovacool, Kelly and Koparde, Vishal and Kuhn, Skyler and Tandon, Mayank and Huse, Susan},
doi = {10.5281/zenodo.13377166},
month = {5},
title = {CCBR Tools: Utilities for CCBR Bioinformatics Software},
url = {https://ccbr.github.io/Tools/},
year = {2025}
}
```
