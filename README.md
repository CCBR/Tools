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

    Traceback (most recent call last):
      File "/opt/hostedtoolcache/Python/3.11.12/x64/bin/ccbr_tools", line 5, in <module>
        from ccbr_tools.__main__ import main
      File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/__main__.py", line 17, in <module>
        from .software import install as install_software
      File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/software.py", line 1, in <module>
        from .pipeline.hpc import Cluster
      File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/__init__.py", line 14, in <module>
        class Pipeline:
      File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/__init__.py", line 18, in Pipeline
        def create(pipeline_name, pipelines=PIPELINES):
                                            ^^^^^^^^^
    NameError: name 'PIPELINES' is not defined

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

Traceback (most recent call last): File
“/opt/hostedtoolcache/Python/3.11.12/x64/bin/ccbr_tools”, line 5, in
<module> from ccbr_tools.\_\_main\_\_ import main File
“/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/**main**.py”,
line 17, in <module> from .software import install as install_software
File
“/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/software.py”,
line 1, in <module> from .pipeline.hpc import Cluster File
“/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/**init**.py”,
line 14, in <module> class Pipeline: File
“/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/**init**.py”,
line 18, in Pipeline def create(pipeline_name, pipelines=PIPELINES):
^^^^^^^^^ NameError: name ‘PIPELINES’ is not defined

### Bibtex entry

```bibtex
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.12/x64/bin/ccbr_tools", line 5, in <module>
    from ccbr_tools.__main__ import main
  File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/__main__.py", line 17, in <module>
    from .software import install as install_software
  File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/software.py", line 1, in <module>
    from .pipeline.hpc import Cluster
  File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/__init__.py", line 14, in <module>
    class Pipeline:
  File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/ccbr_tools/pipeline/__init__.py", line 18, in Pipeline
    def create(pipeline_name, pipelines=PIPELINES):
                                        ^^^^^^^^^
NameError: name 'PIPELINES' is not defined
```
