---
allowed-tools: Bash(git status), Bash(git pull:*), Bash(git checkout:*), Bash(git commit:*), Bash(git tag:*), Bash(git rm:*), Bash(git cherry-pick:*), Bash(git log:*), Bash(git branch:*), Bash(gh run list:*), Bash(gh run watch:*), Bash(hatch version:*), Bash(hatch --env develop run:*), Bash(echo:*), Bash(ls:*), Bash(grep:*), LS, Read
description: Execute automated patch release with QA monitoring and master integration
---

# Release Patch

**NOTE: This is an experimental workflow! If anything seems unclear or missing,
please stop for consultation with the user.**

For execution of a fully-automated postrelease patch.

Below is a validated process to create patch releases with automated monitoring
and clean integration back to master.

Target release version: `$ARGUMENTS` (e.g., `1.24`, `2.3`)

**CRITICAL**: Verify exactly one target release version provided.
**HALT if**:
- No target release version is provided
- Multiple release versions provided (e.g., `1.6 foo bar`)
- Release version format doesn't match `X.Y` pattern (e.g., `1.6.2`, `1.6a0`)

## Context

- Current git status: !`git status`
- Current branch: !`git branch --show-current`
- Current version: !`hatch version`
- Recent commits: !`git log --oneline -10`
- Available towncrier fragments: !`ls .auxiliary/data/towncrier/*.rst 2>/dev/null || echo "No fragments found"`
- Target release branch status: !`git branch -r | grep release-$ARGUMENTS || echo "Release branch not found"`

## Prerequisites

Before running this command, ensure:
- GitHub CLI (`gh`) is installed and authenticated
- Release branch exists for the target version (e.g., `release-1.24` for version `1.24`)
- Working directory is clean with no uncommitted changes
- Towncrier news fragments are present for the patch changes

## Process Summary

Key functional areas of the process:

1. **Branch Setup**: Checkout and update the appropriate release branch
2. **Version Bump**: Increment to next patch version with `hatch version patch`
3. **Update Changelog**: Run Towncrier to build patch changelog
4. **QA Monitoring**: Push commits and monitor QA workflow with GitHub CLI
5. **Tag Release**: Create signed git tag after QA passes
6. **Release Monitoring**: Monitor release workflow deployment
7. **Cleanup**: Remove news fragments and cherry-pick back to master

## Safety Requirements

**CRITICAL**: You MUST halt the process and consult with the user if ANY of the following occur:

- **Step failures**: If any command fails, git operation errors, or tests fail
- **Workflow failures**: If QA or release workflows show failed jobs
- **Version conflicts**: If patch version doesn't match expected patterns
- **Branch issues**: If release branch doesn't exist or is in unexpected state
- **Network issues**: If GitHub operations timeout or fail repeatedly

**Your responsibilities**:
- Validate each step succeeds before proceeding to the next
- Monitor workflow status and halt on any failures
- Provide clear progress updates throughout the process
- Maintain clean git hygiene and proper branching
- Use your judgment to assess when manual intervention is needed

## Release Process

Execute the following steps for target release version `$ARGUMENTS`:

### 1. Pre-Release Quality Check
Run local quality assurance to catch issues early:
```bash
git status && git pull origin master
hatch --env develop run linters
hatch --env develop run testers
hatch --env develop run docsgen
```

### 2. Release Branch Setup
Checkout the target release branch:
```bash
git checkout release-$ARGUMENTS
git pull origin release-$ARGUMENTS
```

### 3. Patch Integration
**Determine patch location and integrate if needed:**

### 3.1. Identify Patch Commits
Before cherry-picking, identify which commits contain actual patch fixes vs. maintenance:

```bash
git log --oneline master
git log --graph --oneline master --since="1 month ago"
# Show commits on master not on release branch
git log --oneline release-$ARGUMENTS..master --since="1 month ago"
```

**Patch commits** (always cherry-pick):
- Bug fixes
- Security patches
- Critical functionality fixes

**Maintenance commits** (evaluate case-by-case):
- Template updates
- Dependency bumps
- Documentation changes

Use `git show <commit>` to review each commit's content before deciding.

**If patches were developed on master** (cherry-pick to release branch):
```bash
# Cherry-pick patch commits from master to release branch
# Use git log --oneline master to identify relevant commit hashes
git cherry-pick <patch-commit-hash-1>
git cherry-pick <patch-commit-hash-2>
# Repeat for all patch commits
```

**If patches were developed on release branch**: Skip this step - patches are already present.

### 4. Pre-Release Validation
Run linting to catch issues before formal release process:
```bash
hatch --env develop run linters
```
**HALT if any linting errors** - fix issues before proceeding.

### 5. Version Management
Increment to next patch version:
```bash
hatch version patch
git commit -am "Version: $(hatch version)"
```

### 6. Changelog Generation
```bash
hatch --env develop run towncrier build --keep --version $(hatch version)
git commit -am "Update changelog for v$(hatch version) patch release."
```

### 7. Quality Assurance Phase
Push branch and monitor QA workflow:
```bash
git push origin release-$ARGUMENTS

# Monitor QA workflow - get run ID from output
gh run list --workflow=qa --limit=1
gh run watch <qa-run-id> --interval 30 --compact
```
**CRITICAL - DO NOT PROCEED UNTIL WORKFLOW COMPLETES:**
- Monitor QA workflow with `gh run watch`
- Use `timeout: 300000` (5 minutes) parameter in Bash tool for monitoring commands
- If command times out, immediately rerun `gh run watch` until completion
- Only proceed to next step after seeing "✓ [workflow-name] completed with 'success'"
- HALT if any jobs fail - consult user before proceeding

### 8. Release Deployment
**Verify QA passed before proceeding to release tag:**
```bash
git tag -m "Release v$(hatch version) patch: <brief-description>." v$(hatch version)
git push --tags

gh run list --workflow=release --limit=1
gh run watch <release-run-id> --interval 30 --compact
```
**CRITICAL - DO NOT PROCEED UNTIL WORKFLOW COMPLETES:**
- Monitor release workflow with `gh run watch`
- Use `timeout: 600000` (10 minutes) parameter in Bash tool for monitoring commands
- If command times out, immediately rerun `gh run watch` until completion
- Only proceed to next step after seeing "✓ [workflow-name] completed with 'success'"
- HALT if any jobs fail - consult user before proceeding

### 9. Post-Release Cleanup
```bash
git rm .auxiliary/data/towncrier/*.rst
git commit -m "Clean up news fragments."
git push origin release-$ARGUMENTS
```

### 10. Master Branch Integration
Cherry-pick commits back to master based on patch development location:

**If patches were developed on master**: Cherry-pick changelog and cleanup commits:
```bash
git checkout master && git pull origin master
git cherry-pick <changelog-commit-hash>
git cherry-pick <cleanup-commit-hash>
git push origin master
```

**If patches were developed on release branch**: Cherry-pick patch, changelog, and cleanup commits:
```bash
git checkout master && git pull origin master
git cherry-pick <patch-commit-hash-1>
git cherry-pick <patch-commit-hash-2>
# Repeat for all patch commits
git cherry-pick <changelog-commit-hash>
git cherry-pick <cleanup-commit-hash>
git push origin master
```

**Note**: Use `git log --oneline` to identify commit hashes for cherry-picking.
