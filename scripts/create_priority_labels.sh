#!/usr/bin/env bash

cmd="gh"
[[ $(type -P "$cmd") ]] && echo "$cmd is in PATH"  ||
    { echo "$cmd is NOT in PATH. Install gh cli first" 1>&2; exit 1; }

reponame=$(gh repo view --json name -q ".name")

gh label create LowPriority --color "#F4C445" --repo "$repo" --force
gh label create MediumPriority --color "#0AB5F4" --repo "$repo" --force
gh label create HighPriority --color "#58E30B" --repo "$repo" --force
