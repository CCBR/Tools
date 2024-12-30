#!/usr/bin/env bash
# check if gh cli is installed
cmd="gh"
[[ $(type -P "$cmd") ]] && echo "$cmd is in PATH"  ||
    { echo "$cmd is NOT in PATH. Install gh cli first" 1>&2; exit 1; }

# get the name of the repo
reponame=$(gh repo view --json name -q ".name")

# add new priority lables
gh label create LowPriority --color "#F4C445" --repo "$repo" --force
gh label create MediumPriority --color "#0AB5F4" --repo "$repo" --force
gh label create HighPriority --color "#58E30B" --repo "$repo" --force
