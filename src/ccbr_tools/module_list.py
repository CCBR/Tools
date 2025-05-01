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
    [
        {
            "name": "rclone",
            "version": "1.70.0-beta"
        },
        {
            "name": "ccbrpipeliner",
            "version": "7"
        },
        {
            "name": "snakemake",
            "version": "7.32.4"
        },
        {
            "name": "singularity",
            "version": "4.2.2"
        }
    ]

    $ module_list snakemake
    7.32.4

    $ module_list python
    not_loaded
"""



import sys
import re
import subprocess
import json

def get_loaded_modules():
    try:
        # Execute 'module list' within a shell and capture stderr
        result = subprocess.run(
            "module list",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # 'module list' outputs to stderr
        output = result.stderr
        return output
    except Exception as e:
        print(f"Error executing 'module list': {e}")
        return ""

def parse_modules(output):
    modules = {}
    # Regular expression to match module entries like '1) module_name/version'
    pattern = re.compile(r'\d+\)\s+([\w\-/\.]+)')
    matches = pattern.findall(output)
    for module_info in matches:
        # Split module name and version
        if '/' in module_info:
            name, version = module_info.rsplit('/', 1)
        else:
            name, version = module_info, ""
        modules[name] = version
    return modules

def print_help():
    help_message = """
Usage:
  module_list           # List all loaded modules in JSON format
  module_list <module>  # Get version of a specific loaded module
  module_list -h | --help  # Show this help message
"""
    print(help_message.strip())

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        # No arguments provided; print all loaded modules in JSON format
        output = get_loaded_modules()
        modules = parse_modules(output)
        module_list = [{'name': name, 'version': version} for name, version in modules.items()]
        print(json.dumps(module_list, indent=4))
    elif len(args) == 1:
        if args[0] in ("-h", "--help"):
            # Help flag provided; print help message
            print_help()
        else:
            # Single argument provided; check if the module is loaded
            module_name = args[0]
            output = get_loaded_modules()
            modules = parse_modules(output)
            version = modules.get(module_name)
            if version:
                print(version)
            else:
                print("not_loaded")
    else:
        # More than one argument provided; print usage information
        print("Error: Too many arguments provided.")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
