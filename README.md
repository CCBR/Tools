<!-- README.md is generated from README.qmd. Please edit that file -->

# CCBR Tools

Utilities for CCBR Bioinformatics Software

[![build](https://github.com/CCBR/Tools/actions/workflows/build-python.yml/badge.svg)](https://github.com/CCBR/Tools/actions/workflows/build-python.yml)
[![codecov](https://codecov.io/gh/CCBR/Tools/graph/badge.svg?token=O73NOR65B3)](https://codecov.io/gh/CCBR/Tools)

## Installation

```sh
pip install git+https://github.com/CCBR/Tools
```

## Usage

```python
!ccbr_tools --help
```

    Usage: ccbr_tools [OPTIONS] COMMAND [ARGS]...

      Utilities for CCBR Bioinformatics Software

      For more options, run: tool_name [command] --help

    Options:
      -v, --version  Show the version and exit.
      -h, --help     Show this message and exit.

    Commands:
      cite  Print the citation in the desired format

    All installed tools:
      ccbr_tools
      gb2gtf
      hf
      intersect
      jobby
      jobinfo
      peek

```python
import ccbr_tools.util
print(ccbr_tools.util.get_version())
```

    0.1.0-dev

## CLI Utilities

Command-line utilities that are part of CCBR Tools.

- `ccbr_tools`
- `gb2gtf`
- `hf`
- `intersect`
- `jobby`
- `jobinfo`
- `peek`

## External Scripts

There are additional standalone scripts for various common tasks in
[scripts/](scripts/). They are less robust than the CLI Utilities
included in the package and do no have any unit tests.

- `add_gene_name_to_count_matrix`
- `aggregate_data_tables`
- `argparse`
- `cancel_snakemake_jobs`
- `create_hpc_link`
- `extract_value_from_json`
- `extract_value_from_yaml`
- `filter_bam_by_readids`
- `filter_fastq_by_readids_highmem`
- `filter_fastq_by_readids_highmem_pe`
- `gather_cluster_stats`
- `gather_cluster_stats_biowulf`
- `get_buyin_partition_list`
- `get_slurm_file_with_error`
- `gsea_preranked`
- `karyoploter`
- `make_labels_for_pipeliner`
- `rawcounts2normalizedcounts_DESeq2`
- `rawcounts2normalizedcounts_limmavoom`
- `run_jobby_on_nextflow_log`
- `run_jobby_on_nextflow_log_full_format`
- `run_jobby_on_snakemake_log`
- `run_jobby_on_snakemake_log_full_format`
- `which_vpn`

## Citation

Please cite this software if you use it in a publication:

    Sovacool K., Koparde V., Kuhn S. CCBR Tools: Utilities for CCBR Bioinformatics Software URL: https://ccbr.github.io/Tools/

### Bibtex entry

    @misc{YourReferenceHere,
    author = {Sovacool, Kelly and Koparde, Vishal and Kuhn, Skyler},
    title = {CCBR Tools: Utilities for CCBR Bioinformatics Software},
    url = {https://ccbr.github.io/Tools/}
    }
