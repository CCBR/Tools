#!/usr/bin/env python3
"""
module_list

A command-line utility to display information about currently loaded environment modules.

This script interacts with the system's module management system (e.g., Lmod or Environment Modules)
to retrieve and display information about loaded modules. It supports two primary modes of operation:

1. **List All Loaded Modules**:
   When executed without any arguments, the script lists all currently loaded modules,
   presenting each module's name and version in a structured JSON format.

2. **Check Specific Module**:
   When provided with a single module name as an argument, the script checks whether
   that module is currently loaded:
   - If the module is loaded, its version is printed.
   - If the module is not loaded, the script outputs "not_loaded".

Usage:
    module_list
        Lists all currently loaded modules in JSON format.

    module_list <module_name>
        Checks if <module_name> is loaded and prints its version or "not_loaded".

    module_list -h | --help
        Displays this help message.

Note:
    - The script relies on the 'module' command-line utility to fetch information about
      loaded modules. Ensure that this utility is available in your system's PATH.
    - The 'module list' command typically outputs to stderr; this script captures that
      output to parse module information.
    - The script is designed to work in environments where modules are managed using
      systems like Lmod or Environment Modules, commonly found in HPC environments.

Example:
    $ module_list
    {
        "ccbrpipeliner": "8",
        "snakemake": "7"
    }

    $ module_list snakemake
    7.32.4

    $ module_list python
    not_loaded
"""


import json
import re
import subprocess
import sys

from .pipeline.hpc import list_modules, parse_modules


def print_help():
    help_message = """
Usage:
  module_list           # List all loaded modules in JSON format
  module_list <module>  # Get version of a specific loaded module
  module_list -h | --help  # Show this help message
"""
    print(help_message, end="")


def module_list(module=""):
    """
    Get the list of loaded modules or the version of a specific module.

    Args:
        module (str): The name of the module to check. If empty, all loaded modules are listed.
    Returns:
        output (str): JSON string of loaded modules or the version of the specified module.
    """
    modules = parse_modules(list_modules())
    if not module:
        output = json.dumps(modules, indent=4)
    else:
        version = modules.get(module)
        if version:
            output = version
        else:
            output = "not_loaded"
    return output


def main():
    args = sys.argv
    if "-h" in args or "--help" in args or len(args) > 2:
        print_help()
    else:
        module = args[1] if len(args) == 2 else ""
        ml = module_list(module)
        print(ml)


if __name__ == "__main__":
    main()
