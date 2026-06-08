# Changes Required in ccbr_tools

## Summary

Enhance the `ccbr tools install` command to support the complete release deployment workflow including latest symlink management and final permission locking.

## Files to Modify

### 1. `src/ccbr_tools/software.py`

#### Change 1.1: Update SET_SYMLINK Template

**Current:** Only creates major.minor symlink
**Change:** Fix `rm -if` to `rm -f` and prepare for latest symlink handling

```python
# BEFORE
SET_SYMLINK = """
pushd {BASE_PATH}
rm -if {MAJOR_MINOR_VERSION}
ln -s {HIDDEN_VERSION} {MAJOR_MINOR_VERSION}
chmod -R g+rwX {MAJOR_MINOR_VERSION}
popd"""

# AFTER
SET_SYMLINK = """
pushd {BASE_PATH}
rm -f {MAJOR_MINOR_VERSION}
ln -s {HIDDEN_VERSION} {MAJOR_MINOR_VERSION}
popd"""
```

#### Change 1.2: Add LATEST_SYMLINK Template

**New template:** Creates and manages the latest symlink pointing to major.minor version

```python
LATEST_SYMLINK = """
pushd {BASE_PATH}
rm -f latest
ln -s {MAJOR_MINOR_VERSION} latest
popd"""
```

#### Change 1.3: Update INSTALL_SCRIPT Template

**Current:** Applies group-writable permissions during install
**Change:** Remove intermediate permissions; apply strict final permissions only

```python
# BEFORE
INSTALL_SCRIPT = """{CONDA_ACTIVATE}
{INSTALL}
chmod -R a+rX {PATH}
chmod -R g+rwX {PATH}
chown -R :{GROUP} {PATH}"""

# AFTER
INSTALL_SCRIPT = """{CONDA_ACTIVATE}
{INSTALL}"""
```

#### Change 1.4: Add FINAL_PERMISSIONS Template

**New template:** Applies read-only permissions to the entire deployment

```python
FINAL_PERMISSIONS = """
chown -R :{GROUP} {BASE_PATH}
chmod -R u-w,g-w,o-w,a+rX {BASE_PATH}"""
```

#### Change 1.5: Update install() Function

**Current:** Only creates major.minor symlink
**Change:** Add latest symlink creation and final permissions

```python
def install(
    tool_name,
    version,
    dryrun=True,
    branch_tag=None,
    software_type=None,
    install_script=INSTALL_SCRIPT,
    symlink_script=SET_SYMLINK,
    latest_symlink_script=LATEST_SYMLINK,
    final_permissions_script=FINAL_PERMISSIONS,
    debug=False,
):
    hpc = Cluster.create_hpc(debug=debug)
    tool = Software.create_software(tool_name, version, software_type=software_type)

    script = install_script.format(
        GROUP=hpc.GROUP,
        CONDA_ACTIVATE=hpc.CONDA_ACTIVATE,
        INSTALL=tool.install(hpc, branch_tag=branch_tag),
        PATH=tool.path(hpc),
    )

    if not tool.is_dev_version:
        # Create major.minor symlink
        script += symlink_script.format(
            BASE_PATH=tool.base_path(hpc),
            HIDDEN_VERSION=tool.hidden_version,
            MAJOR_MINOR_VERSION=tool.major_minor,
        )

        # Create latest symlink
        script += latest_symlink_script.format(
            BASE_PATH=tool.base_path(hpc),
            MAJOR_MINOR_VERSION=tool.major_minor,
        )

        # Apply final permissions
        script += final_permissions_script.format(
            GROUP=hpc.GROUP,
            BASE_PATH=tool.base_path(hpc),
        )

    if dryrun:
        print(script)
    else:
        shell_run(script, shell=True, capture_output=False)
```

## Testing Requirements

### Unit Tests

**File:** `tests/test_software.py` (or create if doesn't exist)

Test cases:

1. Verify `SET_SYMLINK` replaces/updates an existing major.minor symlink atomically (`ln -sfn`)
2. Verify `LATEST_SYMLINK` replaces/updates an existing latest symlink atomically (`ln -sfn`)
3. Verify `FINAL_PERMISSIONS` applies correct chmod flags recursively
4. Verify script output for non-dev versions includes all three symlink/permission steps
5. Verify script output for dev versions excludes symlink/permission steps

### Integration Tests

**Prerequisites:** Test in a safe sandbox directory

Test cases:

1. Run install for a non-dev version and verify symlink chain
2. Run install again with different patch version and verify latest points to new version
3. Verify permissions are read-only (`u-w,g-w,o-w,a+rX`)
4. Verify quick rollback works (`rm -f latest && ln -s v2.6 latest`)

### Manual Verification

```bash
# After running: ccbr tools install RENEE v2.7.6
readlink -f /data/CCBR_Pipeliner/Pipelines/RENEE/latest
# Expected: /data/CCBR_Pipeliner/Pipelines/RENEE/.v2.7.6

readlink /data/CCBR_Pipeliner/Pipelines/RENEE/latest
# Expected: v2.7

readlink /data/CCBR_Pipeliner/Pipelines/RENEE/v2.7
# Expected: .v2.7.6

ls -ld /data/CCBR_Pipeliner/Pipelines/RENEE/
# Expected: dr-xr-xr-x (555 permissions)
```

## Implementation Order

1. **Step 1:** Update `SET_SYMLINK` template (fix `rm -if` to `rm -f`)
2. **Step 2:** Remove intermediate permissions from `INSTALL_SCRIPT`
3. **Step 3:** Add `LATEST_SYMLINK` template
4. **Step 4:** Add `FINAL_PERMISSIONS` template
5. **Step 5:** Update `install()` function to use all templates
6. **Step 6:** Add unit tests
7. **Step 7:** Test with actual deployment (sandbox or staging)
8. **Step 8:** Update command help/documentation

## Documentation to Update

- Update `--help` for `ccbr tools install` command
- Update RELEASE_PLAN.md with automated deployment section
- Add examples to tool documentation showing latest symlink usage
- Document permission model changes

## Backwards Compatibility

**Impact:** Non-breaking change

- Existing versions without latest symlink continue to work
- Running install multiple times is safe (idempotent due to `rm -f`)
- Previous deployments remain read-only; can coexist with new ones

**Migration:** No action required for existing deployments

- Old symlink structure (without latest) continues to work
- `latest` symlink added on next release deployment
