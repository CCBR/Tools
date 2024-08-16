# CCBR Tools

<!-- README.md is generated from README.qmd. Please edit that file -->

Utilities for CCBR Bioinformatics Software

[![build](https://github.com/CCBR/Tools/actions/workflows/build-python.yml/badge.svg)](https://github.com/CCBR/Tools/actions/workflows/build-python.yml)
[![codecov](https://codecov.io/gh/CCBR/Tools/graph/badge.svg?token=O73NOR65B3)](https://codecov.io/gh/CCBR/Tools)

## Installation

On biowulf you can access the latest release of `ccbr_tools` by loading
the ccbrpipeliner module:

``` sh
module load ccbrpipeliner
```

Outside of biowulf, you can install the package with pip:

``` sh
pip install git+https://github.com/CCBR/Tools
```

Or specify a specific tagged version or branch:

``` sh
pip install git+https://github.com/CCBR/Tools@main
```

## Usage

### CLI

``` sh
ccbr_tools --help
```

    Usage: ccbr_tools [OPTIONS] COMMAND [ARGS]...

      Utilities for CCBR Bioinformatics Software

      For more options, run: tool_name [command] --help

    Options:
      -v, --version  Show the version and exit.
      -h, --help     Show this message and exit.

    Commands:
      cite     Print the citation in the desired format
      version  Print the version of ccbr_tools

    All installed tools:
      ccbr_tools
      gb2gtf
      hf
      intersect
      jobby
      jobinfo
      peek

### Python

``` python
import ccbr_tools.pkg_util
print(ccbr_tools.pkg_util.get_version())
```

    0.1.0-dev

## CLI Utilities

Command-line utilities in CCBR Tools.

- `ccbr_tools`
- `gb2gtf`
- `hf`
- `intersect`
- `jobby`
- `jobinfo`
- `peek`

Run a command with `--help` to learn how to use it.

## External Scripts

Additional standalone scripts for various common tasks in
[scripts/](scripts/) are added to the path when this package is
installed. They are less robust than the CLI Utilities included in the
package and do not have any unit tests.

- `add_gene_name_to_count_matrix.R`
- `aggregate_data_tables.R`
- `argparse.bash`
- `cancel_snakemake_jobs.sh`
- `create_hpc_link.sh`
- `extract_value_from_json.py`
- `extract_value_from_yaml.py`
- `filter_bam_by_readids.py`
- `filter_fastq_by_readids_highmem.py`
- `filter_fastq_by_readids_highmem_pe.py`
- `gather_cluster_stats.sh`
- `gather_cluster_stats_biowulf.sh`
- `get_buyin_partition_list.bash`
- `get_slurm_file_with_error.sh`
- `gsea_preranked.sh`
- `karyoploter.R`
- `make_labels_for_pipeliner.sh`
- `rawcounts2normalizedcounts_DESeq2.R`
- `rawcounts2normalizedcounts_limmavoom.R`
- `run_jobby_on_nextflow_log`
- `run_jobby_on_nextflow_log_full_format`
- `run_jobby_on_snakemake_log`
- `run_jobby_on_snakemake_log_full_format`
- `spooker`
- `which_vpn.sh`

## Citation

Please cite this software if you use it in a publication:

> Sovacool K., Koparde V., Kuhn S., Tandon M., Huse S. CCBR Tools:
> Utilities for CCBR Bioinformatics Software URL:
> https://ccbr.github.io/Tools/

### Bibtex entry

    @misc{YourReferenceHere,
    author = {Sovacool, Kelly and Koparde, Vishal and Kuhn, Skyler and Tandon, Mayank and Huse, Susan},
    title = {CCBR Tools: Utilities for CCBR Bioinformatics Software},
    url = {https://ccbr.github.io/Tools/}
    }
