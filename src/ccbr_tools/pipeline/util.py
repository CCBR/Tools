"""
Pipeline utility functions
"""

import collections
import datetime
import shutil
import sys
import hashlib
import json
import glob
import os
import re
import stat
import subprocess
import warnings
import yaml

from ..pkg_util import repo_base, msg
from .hpc import get_hpcname


def get_tmp_dir(tmp_dir, outdir, hpc=get_hpcname()):
    """
    Get default temporary directory for biowulf and frce. Allow user override.

    Args:
        tmp_dir (str): User-defined temporary directory path. If provided, this path will be used as the temporary directory.
        outdir (str): Output directory path.
        hpc (str, optional): HPC name. Defaults to the value returned by get_hpcname().
    Returns:
        tmp_dir (str): The default temporary directory path based on the HPC name and user-defined path.
    """
    if not tmp_dir:
        if hpc == "biowulf":
            tmp_dir = "/lscratch/$SLURM_JOBID"
        elif hpc == "frce":
            tmp_dir = outdir
        else:
            tmp_dir = None
    return tmp_dir


def get_genomes_list(repo_base, hpcname=get_hpcname(), error_on_warnings=False):
    """
    Get list of genome annotations available for the current platform

    Args:
        repo_base (str): The base directory of the repository
        hpcname (str, optional): The name of the HPC. Defaults to the value returned by get_hpcname().
        error_on_warnings (bool, optional): Whether to raise an error on warnings. Defaults to False.
    Returns:
        genomes (list): A sorted list of genome annotations available for the current platform
    """
    return sorted(
        list(
            get_genomes_dict(
                repo_base=repo_base,
                hpcname=hpcname,
                error_on_warnings=error_on_warnings,
            ).keys()
        )
    )


def get_genomes_dict(repo_base, hpcname=get_hpcname(), error_on_warnings=False):
    """
    Get dictionary of genome annotation versions and the paths to the corresponding JSON files.

    Args:
        repo_base (function): Function for getting the base directory of the repository.
        hpcname (str, optional): Name of the HPC. Defaults to the value returned by get_hpcname().
        error_on_warnings (bool, optional): Flag to indicate whether to raise warnings as errors. Defaults to False.
    Returns:
        genomes_dict (dict): A dictionary containing genome names as keys and corresponding JSON file paths as values.  { genome_name: json_file_path }
    """
    if error_on_warnings:
        warnings.filterwarnings("error")
    genomes_dir = repo_base("config", "genomes", hpcname)
    if not os.path.exists(genomes_dir):
        warnings.warn(f"Folder does not exist: {genomes_dir}")
    search_term = f"{genomes_dir}/*.json"
    json_files = glob.glob(search_term)
    if len(json_files) == 0:
        warnings.warn(
            f"No Genome+Annotation JSONs found in {genomes_dir}. Please specify a custom genome json file with `--genome`"
        )
    genomes_dict = {
        os.path.basename(json_file).replace(".json", ""): json_file
        for json_file in json_files
    }
    warnings.resetwarnings()
    return genomes_dict


def md5sum(filename, first_block_only=False, blocksize=65536):
    """Gets md5checksum of a file in memory-safe manner.
    The file is read in blocks/chunks defined by the blocksize parameter. This is
    a safer option to reading the entire file into memory if the file is very large.
    @param filename <str>:
        Input file on local filesystem to find md5 checksum
    @param first_block_only <bool>:
        Calculate md5 checksum of the first block/chunk only
    @param blocksize <int>:
        Blocksize of reading N chunks of data to reduce memory profile
    @return hasher.hexdigest() <str>:
        MD5 checksum of the file's contents
    """
    hasher = hashlib.md5()
    with open(filename, "rb") as fh:
        buf = fh.read(blocksize)
        if first_block_only:
            # Calculate MD5 of first block or chunk of file.
            # This is a useful heuristic for when potentially
            # calculating an MD5 checksum of thousand or
            # millions of file.
            hasher.update(buf)
            return hasher.hexdigest()
        while len(buf) > 0:
            # Calculate MD5 checksum of entire file
            hasher.update(buf)
            buf = fh.read(blocksize)

    return hasher.hexdigest()


def permissions(parser, path, *args, **kwargs):
    """Checks permissions using os.access() to see the user is authorized to access
    a file/directory. Checks for existence, readability, writability and executability via:
    os.F_OK (tests existence), os.R_OK (tests read), os.W_OK (tests write), os.X_OK (tests exec).
    @param parser <argparse.ArgumentParser() object>:
        Argparse parser object
    @param path <str>:
        Name of path to check
    @return path <str>:
        Returns abs path if it exists and permissions are correct
    """
    if not exists(path):
        parser.error(
            "Path '{}' does not exists! Failed to provide valid input.".format(path)
        )
    if not os.access(path, *args, **kwargs):
        parser.error(
            "Path '{}' exists, but cannot read path due to permissions!".format(path)
        )

    return os.path.abspath(path)


def standard_input(parser, path, *args, **kwargs):
    """Checks for standard input when provided or permissions using permissions().
    @param parser <argparse.ArgumentParser() object>:
        Argparse parser object
    @param path <str>:
        Name of path to check
    @return path <str>:
        If path exists and user can read from location
    """
    # Checks for standard input
    if not sys.stdin.isatty():
        # Standard input provided, set path as an
        # empty string to prevent searching of '-'
        path = ""
        return path

    # Checks for positional arguments as paths
    path = permissions(parser, path, *args, **kwargs)

    return path


def exists(testpath):
    """Checks if file exists on the local filesystem.
    @param parser <argparse.ArgumentParser() object>:
        argparse parser object
    @param testpath <str>:
        Name of file/directory to check
    @return does_exist <boolean>:
        True when file/directory exists, False when file/directory does not exist
    """
    does_exist = True
    if not os.path.exists(testpath):
        does_exist = False  # File or directory does not exist on the filesystem

    return does_exist


def ln(files, outdir):
    """Creates symlinks for files to an output directory.
    @param files list[<str>]:
        List of filenames
    @param outdir <str>:
        Destination or output directory to create symlinks
    """
    # Create symlinks for each file in the output directory
    for file in files:
        ln = os.path.join(outdir, os.path.basename(file))
        if not exists(ln):
            os.symlink(os.path.abspath(os.path.realpath(file)), ln)


def which(cmd, path=None):
    """Checks if an executable is in $PATH
    @param cmd <str>:
        Name of executable to check
    @param path <list>:
        Optional list of PATHs to check [default: $PATH]
    @return <boolean>:
        True if exe in PATH, False if not in PATH
    """
    if path is None:
        path = os.environ["PATH"].split(os.pathsep)

    for prefix in path:
        filename = os.path.join(prefix, cmd)
        executable = os.access(filename, os.X_OK)
        is_not_directory = os.path.isfile(filename)
        if executable and is_not_directory:
            return True
    return False


def err(*message, **kwargs):
    """Prints any provided args to standard error.
    kwargs can be provided to modify print functions
    behavior.
    @param message <any>:
        Values printed to standard error
    @params kwargs <print()>
        Key words to modify print function behavior
    """
    print(*message, file=sys.stderr, **kwargs)


def fatal(*message, **kwargs):
    """Prints any provided args to standard error
    and exits with an exit code of 1.
    @param message <any>:
        Values printed to standard error
    @params kwargs <print()>
        Key words to modify print function behavior
    """
    err(*message, **kwargs)
    sys.exit(1)


def require(cmds, suggestions, path=None):
    """Enforces an executable is in $PATH
    @param cmds list[<str>]:
        List of executable names to check
    @param suggestions list[<str>]:
        Name of module to suggest loading for a given index
        in param cmd.
    @param path list[<str>]]:
        Optional list of PATHs to check [default: $PATH]
    """
    error = False
    for i in range(len(cmds)):
        available = which(cmds[i])
        if not available:
            error = True
            err(
                """\x1b[6;37;41m\n\tFatal: {} is not in $PATH and is required during runtime!
            └── Solution: please 'module load {}' and run again!\x1b[0m""".format(
                    cmds[i], suggestions[i]
                )
            )

    if error:
        fatal()

    return


def safe_copy(source, target, resources=[]):
    """Private function: Given a list paths it will recursively copy each to the
    target location. If a target path already exists, it will NOT over-write the
    existing paths data.
    @param resources <list[str]>:
        List of paths to copy over to target location
    @params source <str>:
        Add a prefix PATH to each resource
    @param target <str>:
        Target path to copy templates and required resources
    """

    for resource in resources:
        destination = os.path.join(target, resource)
        if not exists(destination):
            # Required resources do not exist
            shutil.copytree(os.path.join(source, resource), destination)


def git_commit_hash(repo_path):
    """Gets the git commit hash of the RNA-seek repo.
    @param repo_path <str>:
        Path to RNA-seek git repo
    @return githash <str>:
        Latest git commit hash
    """
    try:
        githash = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT, cwd=repo_path
            )
            .strip()
            .decode("utf-8")
        )
        # Typecast to fix python3 TypeError (Object of type bytes is not JSON serializable)
        # subprocess.check_output() returns a byte string
        githash = str(githash)
    except Exception as e:
        # Github releases are missing the .git directory,
        # meaning you cannot get a commit hash, set the
        # commit hash to indicate its from a GH release
        githash = "github_release"
    return githash


def join_jsons(templates):
    """Joins multiple JSON files to into one data structure
    Used to join multiple template JSON files to create a global config dictionary.
    @params templates <list[str]>:
        List of template JSON files to join together
    @return aggregated <dict>:
        Dictionary containing the contents of all the input JSON files
    """
    # Get absolute PATH to templates in rna-seek git repo
    repo_path = os.path.dirname(os.path.abspath(__file__))
    aggregated = {}

    for file in templates:
        with open(os.path.join(repo_path, file), "r") as fh:
            aggregated.update(json.load(fh))

    return aggregated


def check_python_version(MIN_PYTHON=(3, 11)):
    # version check
    # glob.iglob requires 3.11 for using "include_hidden=True"
    try:
        assert sys.version_info >= MIN_PYTHON
        print(
            "Python version: {0}.{1}.{2}".format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro
            )
        )
    except AssertionError:
        exit(
            f"{sys.argv[0]} requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"
        )


def _get_file_mtime(f):
    timestamp = datetime.fromtimestamp(os.path.getmtime(os.path.abspath(f)))
    mtime = timestamp.strftime("%y%m%d%H%M%S")
    return mtime


def _cp_r_safe_(
    source, target, resources=["workflow", "resources", "config"], safe_mode=True
):
    """Private function: Given a list paths it will recursively copy each to the
    target location. If a target path already exists, it will not over-write the
    existing paths data when `safe_mode` is on.
    @param resources <list[str]>:
        List of paths to copy over to target location.
        Default: ["workflow", "resources", "config"]
    @params source <str>:
        Add a prefix PATH to each resource
    @param target <str>:
        Target path to copy templates and required resources (aka destination)
    @param safe_mode <bool>:
        Only copy the resources to the target path
        if they do not exist in the target path (default: True)
    """
    for resource in resources:
        destination = os.path.join(target, resource)
        if os.path.exists(destination) and safe_mode:
            print(f"🚫 path exists and `safe_mode` is ON, not copying: {destination}")
        else:
            # Required resources do not exist, or safe mode is off
            shutil.copytree(
                os.path.join(source, resource), destination, dirs_exist_ok=not safe_mode
            )


def _sym_safe_(input_data, target):
    """Creates re-named symlinks for each FastQ file provided
    as input. If a symlink already exists, it will not try to create a new symlink.
    If relative source PATH is provided, it will be converted to an absolute PATH.
    @param input_data <list[<str>]>:
        List of input files to symlink to target location
    @param target <str>:
        Target path to copy templates and required resources
    @return input_fastqs list[<str>]:
        List of renamed input FastQs
    """
    input_fastqs = []  # store renamed fastq file names
    for file in input_data:
        filename = os.path.basename(file)
        renamed = os.path.join(target, rename(filename))
        input_fastqs.append(renamed)

        if not os.path.exists(renamed):
            # Create a symlink if it does not already exist
            # Follow source symlinks to resolve any binding issues
            os.symlink(os.path.abspath(os.path.realpath(file)), renamed)

    return input_fastqs


def rename(filename):
    """Dynamically renames FastQ file to have one of the following extensions: *.R1.fastq.gz, *.R2.fastq.gz
    To automatically rename the fastq files, a few assumptions are made. If the extension of the
    FastQ file cannot be inferred, an exception is raised telling the user to fix the filename
    of the fastq files.
    @param filename <str>:
        Original name of file to be renamed
    @return filename <str>:
        A renamed FastQ filename
    """
    # Covers common extensions from SF, SRA, EBI, TCGA, and external sequencing providers
    # key = regex to match string and value = how it will be renamed
    extensions = {
        # Matches: _R[12]_fastq.gz, _R[12].fastq.gz, _R[12]_fq.gz, etc.
        ".R1.f(ast)?q.gz$": ".R1.fastq.gz",
        ".R2.f(ast)?q.gz$": ".R2.fastq.gz",
        # Matches: _R[12]_001_fastq_gz, _R[12].001.fastq.gz, _R[12]_001.fq.gz, etc.
        # Capture lane information as named group
        ".R1.(?P<lane>...).f(ast)?q.gz$": ".R1.fastq.gz",
        ".R2.(?P<lane>...).f(ast)?q.gz$": ".R2.fastq.gz",
        # Matches: _[12].fastq.gz, _[12].fq.gz, _[12]_fastq_gz, etc.
        "_1.f(ast)?q.gz$": ".R1.fastq.gz",
        "_2.f(ast)?q.gz$": ".R2.fastq.gz",
    }

    if filename.endswith(".R1.fastq.gz") or filename.endswith(".R2.fastq.gz"):
        # Filename is already in the correct format
        return filename

    converted = False
    for regex, new_ext in extensions.items():
        matched = re.search(regex, filename)
        if matched:
            # regex matches with a pattern in extensions
            converted = True
            # Try to get substring for named group lane, retain this in new file extension
            # Come back to this later, I am not sure if this is necessary
            # That string maybe static (i.e. always the same)
            # https://support.illumina.com/help/BaseSpace_OLH_009008/Content/Source/Informatics/BS/NamingConvention_FASTQ-files-swBS.htm#
            try:
                new_ext = "_{}{}".format(matched.group("lane"), new_ext)
            except IndexError:
                pass  # Does not contain the named group lane

            filename = re.sub(regex, new_ext, filename)
            break  # only rename once

    if not converted:
        raise NameError(
            """\n\tFatal: Failed to rename provided input '{}'!
        Cannot determine the extension of the user provided input file.
        Please rename the file list above before trying again.
        Here is example of acceptable input file extensions:
          sampleName.R1.fastq.gz      sampleName.R2.fastq.gz
          sampleName_R1_001.fastq.gz  sampleName_R2_001.fastq.gz
          sampleName_1.fastq.gz       sampleName_2.fastq.gz
        Please also check that your input files are gzipped?
        If they are not, please gzip them before proceeding again.
        """.format(
                filename
            )
        )

    return filename


def copy_config(config_paths, overwrite=True, repo_base=repo_base):
    msg("Copying default config files to current working directory")
    for local_config in config_paths:
        system_config = repo_base(local_config)
        if os.path.isfile(system_config):
            shutil.copyfile(system_config, local_config)
        elif os.path.isdir(system_config):
            shutil.copytree(system_config, local_config, dirs_exist_ok=overwrite)
        else:
            raise FileNotFoundError(f"Cannot copy {system_config} to {local_config}")


def read_config_yml(file):
    with open(file, "r") as stream:
        _config = yaml.safe_load(stream)
    return _config


def update_config(config, overwrite_config):
    def _update(d, u):
        for key, value in u.items():
            if isinstance(value, collections.abc.Mapping):
                d[key] = _update(d.get(key, {}), value)
            else:
                d[key] = value
        return d

    _update(config, overwrite_config)


def write_config_yml(_config, file):
    msg(f"Writing runtime config file to {file}")
    with open(file, "w") as stream:
        yaml.dump(_config, stream)


def chmod_bins_exec(repo_base=repo_base):
    """Ensure that all files in bin/ are executable.

    It appears that setuptools strips executable permissions from package_data files,
    yet post-install scripts are not possible with the pyproject.toml format.
    Without this hack, nextflow processes that call scripts in bin/ fail.

    https://stackoverflow.com/questions/18409296/package-data-files-with-executable-permissions
    https://github.com/pypa/setuptools/issues/2041
    https://stackoverflow.com/questions/76320274/post-install-script-for-pyproject-toml-projects
    """
    bin_dir = repo_base("bin/")
    for filename in os.listdir(bin_dir):
        bin_path = os.path.join(bin_dir, filename)
        if os.path.isfile(bin_path):
            file_stat = os.stat(bin_path)
            # below is equivalent to `chmod +x`
            os.chmod(
                bin_path, file_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )
