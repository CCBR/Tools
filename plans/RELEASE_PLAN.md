# Generic Release Plan for CCBR Pipeline/Tool Deployment

## Overview

This plan standardizes the deployment process for all CCBR pipelines and tools, ensuring consistent symlink management and permission handling across environments.

## Deployment Architecture

```
/data/CCBR_Pipeliner/Pipelines/{PIPELINE_NAME}/
├── latest/ → v2.7 (user-facing endpoint, read-only)
├── v2.7/ → .v2.7.6 (major.minor version symlink, read-only)
└── .v2.7.6/ (hidden version directory, read-only)
    ├── VERSION
    ├── bin/
    ├── lib/
    └── ...
```

## Release Process (5 Steps)

### Step 1: Clone Release Tag to Hidden Version Directory

**Action:** Clone the specific version tag into `.v{VERSION}` directory

```bash
git clone --depth 1 --branch v2.7.6 https://github.com/CCBR/RENEE.git .v2.7.6
```

**Group:** `CCBR_Pipeliner`

### Step 2: Create Major.Minor Symlink

**Action:** Atomically create/update symlink from `v{MAJOR}.{MINOR}` → `.v{VERSION}`

```bash
cd /data/CCBR_Pipeliner/Pipelines/RENEE/
ln -sfn .v2.7.6 v2.7
```

**Purpose:** Allows multiple patch versions under one major.minor ref; atomic operation prevents race conditions
**Note:** `-sfn` flag replaces existing link and handles non-existent files safely

### Step 3: Create Latest Symlink

**Action:** Atomically create/update symlink from `latest` → `v{MAJOR}.{MINOR}`

```bash
ln -sfn v2.7 latest
```

**Purpose:** Single user-facing entry point that points to the active major.minor version; atomic operation prevents race conditions

### Step 4: Verify Symlink Chain

**Action:** Confirm the full chain resolves correctly

```bash
readlink -f latest  # should resolve to /data/.../RENEE/.v2.7.6
```

### Step 5: Apply Final Permissions & Ownership

**Action:** Recursively lock down permissions and set group ownership

```bash
chown -R :CCBR_Pipeliner /data/CCBR_Pipeliner/Pipelines/RENEE/
chmod -R u-w,g-w,o-w,a+rX /data/CCBR_Pipeliner/Pipelines/RENEE/
```

**Recursive Permission Changes:**

`chown -R :CCBR_Pipeliner`:

- Changes group ownership to `CCBR_Pipeliner` for:
  - All files in `.v2.7.6/` and all subdirectories
  - Symlink targets (the directories/files they point to), not the symlinks themselves
  - Note: On most systems, symlink ownership doesn't affect access (target permissions are used)

`chmod -R u-w,g-w,o-w,a+rX`:

- **Files**:
  - Remove write permission for user, group, others
  - Add read permission for all
  - Add execute only if already executable (capital X prevents making non-executables executable)
  - Before: `-rw-r--r--` (644)
  - After: `-r--r--r--` (444) or `-r-xr-xr-x` (555) if originally executable
- **Directories**:
  - Remove write permission for user, group, others
  - Add read+execute for all (needed for traversal)
  - Before: `drwxr-xr-x` (755)
  - After: `dr-xr-xr-x` (555)
- **Symlinks**:
  - Permissions unchanged (symlinks don't use permissions on most systems)

**Result:**

- All files become read-only (no write for anyone)
- All directories become read-only with execute (for traversal)
- No one can modify, delete, or rename anything under `/data/CCBR_Pipeliner/Pipelines/RENEE/`
- Prevents accidental modifications; requires `sudo` or explicit `chmod` to update

### Step 7: Verify Symlink Chain & Deployment

**Action:** Confirm the full chain resolves and works correctly

```bash
readlink -f latest  # should resolve to /data/.../RENEE/.v2.7.6
/data/CCBR_Pipeliner/Pipelines/RENEE/latest/bin/renee --help
/data/CCBR_Pipeliner/Pipelines/RENEE/latest/bin/renee --version
```

**Expected Output:**

- readlink: `/data/CCBR_Pipeliner/Pipelines/RENEE/.v2.7.6`
- help: No ModuleNotFoundError; command runs cleanly
- version: `2.7.6`

## Permission Model

All deployed releases are **read-only for all users**:

| Entity             | Before | After           |
| ------------------ | ------ | --------------- |
| User write         | ✓      | ✗               |
| Group write        | ✓      | ✗               |
| Others write       | ✓      | ✗               |
| All read           | ✓      | ✓               |
| All execute (dirs) | ✓      | ✓               |
| Execute (files)    | ✓/✗    | ✓/✗ (unchanged) |

This prevents accidental modifications and requires explicit permission escalation for maintenance or updates.

## Rollback Procedure

### Quick Rollback (revert to previous major.minor)

```bash
cd /data/CCBR_Pipeliner/Pipelines/{PIPELINE_NAME}/
rm -f latest
ln -s v2.6 latest
```

### Full Rollback (remove a release)

```bash
cd /data/CCBR_Pipeliner/Pipelines/{PIPELINE_NAME}/
rm -f latest
ln -s v2.6 latest
rm -rf .v2.7.6  # only if confirmed no active uses
```

## Automated Deployment via `ccbr tools install`

The `ccbr tools install` command automates this entire process:

```bash
ccbr tools install RENEE v2.7.6
```

Internally executes:

1. Clone into `.v2.7.6`
2. Delete `v2.7` symlink if exists
3. Create `v2.7` symlink
4. Delete `latest` symlink if exists
5. Create `latest` symlink
6. Recursively apply permissions and ownership

## Implementation Notes

- **Non-Dev Versions Only:** Symlink creation only occurs for releases (not dev/pre-release versions)
- **Idempotent:** Can be run multiple times safely; always deletes old symlinks before creating new ones
- **Atomic:** All steps happen in sequence; failures halt the process
- **Reversible:** Symlinks can be quickly reverted without removing source code

## Multi-Version Support

Multiple minor versions can coexist:

```
/data/CCBR_Pipeliner/Pipelines/RENEE/
├── latest → v2.7
├── v2.7 → .v2.7.6
├── v2.6 → .v2.6.8
├── .v2.7.6/
└── .v2.6.8/
```

Users can target specific major.minor versions while `latest` tracks the current production release.
