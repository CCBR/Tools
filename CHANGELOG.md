## Tools development version

## Tools 0.2.0

- new commands:
  - `ccbr_tools send-email` for sending emails from the command line. (#26, @kelly-sovacool)
    - With new helper function: `send_email.send_email_msg()`.
    - Works when run from biowulf.
  - `ccbr_tools quarto-add` to add quarto extensions from this package. (#30, @kelly-sovacool)
    - Includes new format `fnl` for our documentation websites.
- new functions for creating a contributors page for documentation websites: `github.print_contributor_images()`. (#27, @kelly-sovacool)
- new script from [`CCBR/TaskManagement`](https://github.com/CCBR/TaskManagement/tree/103c73d41858d400fba95ed2130d7d5653f243e0/scripts): `github_milestones.sh`. (#29, @kelly-sovacool)
- documentation improvements:
  - fix docstrings rendering -- use Google style. (#25, @kelly-sovacool)
  - overhaul navigation structure of docs website. (#28, @kelly-sovacool)
  - style the website to follow FNL branding guidelines. (#30, @kelly-sovacool)
  - miscellaneous minor improvements. (#32, @kelly-sovacool)
- bug fixes:
  - include data files in package installation for `homologfinder`. (#31, @kelly-sovacool)

## Tools 0.1.4

- fix copy location for spook. (@kopardev)

## Tools 0.1.3

- fix shared SIF cache directory spelling for biowulf. (#23, @kelly-sovacool)

## Tools 0.1.2

- use major & minor version for docs website subdirectories. (#15, @kelly-sovacool)
- fig bug where `nextflow.run()` did not import the correct HPC modules. (#20, @kelly-sovacool)
- fix bug in `_get_file_mtime()`. (#21, @kelly-sovacool)

## Tools 0.1.1

- fix: don't add extra newline to command stdout/stderr for `shell_run()` and `exec_in_context()`. (#10, @kelly-sovacool)
- minor docuemntation improvements. (#12, @kelly-sovacool)

## Tools 0.1.0

The Tools repository is now restructured as a Python package.
All previous python scripts which included command line utilities have been
moved to `src/`, and all other scripts have been moved to `scripts/`.
In both cases, they are available in the path when the package is installed.

Functions which were part of both XAVIER and RENEE are available for re-use in
other bioinformatics pipelines for tasks such as determining the HPC
environment, retrieving available genome annotations, and printing citation and
version information.
Explore the `ccbr_tools` reference documentation for more information:
<https://ccbr.github.io/Tools/reference/>

### CLI Utilities

Command-line utilities in CCBR Tools.

- `ccbr_tools`
- `gb2gtf`
- `hf`
- `intersect`
- `jobby`
- `jobinfo`
- `peek`

Run a command with `--help` to learn how to use it.

### External Scripts

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

## Tools 0.0.1

This tag marks the repository state from before refactoring it as a python package.
