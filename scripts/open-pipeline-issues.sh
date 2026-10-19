#!/usr/bin/env bash
# Open the same GitHub issue in every Snakemake & Nextflow pipeline repo listed in CCBR_SOFTWARE.
# Example
#   bash ./scripts/open-pipeline-issues.sh -t "load apptainer instead of singularity" -b "See https://github.com/CCBR/ccbrpipeliner/issues/92" -l "refactor" -n
set -euo pipefail

usage() {
    cat <<EOF
Usage: $(basename "$0") -t TITLE (-b BODY | -f BODY_FILE) [-l LABEL] [-n]

  -t TITLE      Issue title (required)
  -b BODY       Issue body text
  -f BODY_FILE  Read issue body from a file ('-' for stdin)
  -l LABEL      Label to add (repeatable); created in the repo if missing
  -n            Dry run: print what would be done without creating issues
  -h            Show this help
EOF
}

OWNER="CCBR"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOFTWARE_PY="${SCRIPT_DIR}/../src/ccbr_tools/software.py"

title=""
body=""
body_file=""
dryrun=0
labels=()

while getopts ":t:b:f:l:nh" opt; do
    case "$opt" in
        t) title="$OPTARG" ;;
        b) body="$OPTARG" ;;
        f) body_file="$OPTARG" ;;
        l) labels+=("$OPTARG") ;;
        n) dryrun=1 ;;
        h) usage; exit 0 ;;
        :) echo "Error: -$OPTARG requires an argument" >&2; usage >&2; exit 1 ;;
        \?) echo "Error: invalid option -$OPTARG" >&2; usage >&2; exit 1 ;;
    esac
done

if [[ -z "$title" ]]; then
    echo "Error: title is required" >&2; usage >&2; exit 1
fi
if [[ -n "$body" && -n "$body_file" ]]; then
    echo "Error: use only one of -b or -f" >&2; exit 1
fi
if [[ -z "$body" && -z "$body_file" ]]; then
    echo "Error: a body is required (-b or -f)" >&2; usage >&2; exit 1
fi
if [[ "$body_file" == "-" ]]; then
    body="$(cat)"
elif [[ -n "$body_file" ]]; then
    body="$(cat "$body_file")"
fi

command -v gh >/dev/null || { echo "Error: GitHub CLI 'gh' not found" >&2; exit 1; }
if [[ "$dryrun" -eq 0 || ${#labels[@]} -gt 0 ]]; then
    gh auth status >/dev/null 2>&1 || { echo "Error: run 'gh auth login' first" >&2; exit 1; }
fi

repos=()
while IFS= read -r repo; do
    repos+=("$repo")
done < <(grep -E '^[[:space:]]*"[^"]+":[[:space:]]*(Snakemake|Nextflow),' "$SOFTWARE_PY" | sed -E 's/^[[:space:]]*"([^"]+)".*/\1/')

if [[ ${#repos[@]} -eq 0 ]]; then
    echo "Error: no pipelines found in $SOFTWARE_PY" >&2; exit 1
fi

label_args=()
for label in "${labels[@]+"${labels[@]}"}"; do
    label_args+=(--label "$label")
done

# Returns non-zero if any missing label could not be created.
ensure_labels() {
    local full="$1" existing label
    [[ ${#labels[@]} -eq 0 ]] && return 0
    existing=$(gh label list --repo "$full" --limit 1000 --json name --jq '.[].name') || return 1
    for label in "${labels[@]}"; do
        # GitHub label names are case-insensitive
        if ! grep -Fixq -- "$label" <<<"$existing"; then
            if [[ "$dryrun" -eq 1 ]]; then
                echo "[dry run] would create label '${label}' in ${full}"
            else
                gh label create "$label" --repo "$full" >/dev/null || return 1
                echo "${full}: created label '${label}'"
            fi
        fi
    done
}

failed=()
for repo in "${repos[@]}"; do
    full="${OWNER}/${repo}"
    if ! ensure_labels "$full"; then
        echo "${full}: FAILED to set up labels" >&2
        failed+=("$full")
        continue
    fi
    if [[ "$dryrun" -eq 1 ]]; then
        echo "[dry run] would open issue in ${full}: ${title}"
        continue
    fi
    if url=$(gh issue create --repo "$full" --title "$title" --body "$body" "${label_args[@]+"${label_args[@]}"}"); then
        echo "${full}: ${url}"
    else
        echo "${full}: FAILED" >&2
        failed+=("$full")
    fi
done

if [[ ${#failed[@]} -gt 0 ]]; then
    echo "Failed repos: ${failed[*]}" >&2
    exit 1
fi
