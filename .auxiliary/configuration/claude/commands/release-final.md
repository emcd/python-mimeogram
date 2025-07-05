---
allowed-tools: Bash(git status), Bash(git pull:*), Bash(git checkout:*), Bash(git add:*), Bash(git commit:*), Bash(git tag:*), Bash(git rm:*), Bash(git cherry-pick:*), Bash(git log:*), Bash(git branch:*), Bash(gh run list:*), Bash(gh run watch:*), Bash(hatch version:*), Bash(hatch --env develop run:*), Bash(echo:*), Bash(ls:*), Bash(grep:*), LS, Read
description: Execute automated final release with QA monitoring and development cycle setup
---

# Release Final

**NOTE: This is an experimental workflow! If anything seems unclear or missing,
please stop for consultation with the user.**

For execution of a fully-automated final release.

Below is a validated process to create a final release with automated
monitoring and next development cycle setup.

Target release version: `$ARGUMENTS` (e.g., `1.6`, `2.0`)

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
- Target release branch status: !`git branch -r | grep release-$ARGUMENTS || echo "Release branch not found - will create new"`
- Local release branch status: !`git branch | grep release-$ARGUMENTS || echo "No local release branch"`

## Prerequisites

Before starting, ensure:
- GitHub CLI (`gh`) is installed and authenticated
- For new releases: All changes are committed to `master` branch
- For existing release branches: Release candidate has been validated and tested
- Working directory is clean with no uncommitted changes
- Towncrier news fragments are present for the release enhancements

## Process Summary

Key functional areas of the process:

1. **Branch Setup**: Create new release branch or checkout existing one
2. **Version Bump**: Set version to final release (major/minor/patch as appropriate)
3. **Update Changelog**: Run Towncrier to build final changelog
4. **QA Monitoring**: Push commits and monitor QA workflow with GitHub CLI
5. **Tag Release**: Create signed git tag after QA passes
6. **Release Monitoring**: Monitor release workflow deployment
7. **Cleanup**: Remove news fragments and cherry-pick back to master
8. **Next Development Cycle**: Set up master branch for next development version

## Safety Requirements

**CRITICAL**: You MUST halt the process and consult with the user if ANY of the
following occur:

- **Step failures**: If any command fails, git operation errors, or tests fail
- **Workflow failures**: If QA or release workflows show failed jobs
- **Unexpected output**: If commands produce unclear or concerning results
- **Version conflicts**: If version bumps don't match expected patterns
- **Network issues**: If GitHub operations timeout or fail repeatedly

**Your responsibilities**:
- Validate each step succeeds before proceeding to the next
- Monitor workflow status and halt on any failures
- Provide clear progress updates throughout the process
- Maintain clean git hygiene and proper branching
- Use your judgment to assess when manual intervention is needed

## Release Process

Execute the following steps for target version `$ARGUMENTS`:

### 1. Pre-Release Quality Check
Run local quality assurance to catch issues early:
```bash
git status && git pull origin master
hatch --env develop run linters
hatch --env develop run testers
hatch --env develop run docsgen
```

### 2. Release Branch Setup
Determine release branch name from target version (e.g., `1.6` → `release-1.6`).

**If release branch exists** (for RC→final conversion):
```bash
git checkout release-$ARGUMENTS
git pull origin release-$ARGUMENTS
```

**If creating new release branch**:
```bash
git checkout master && git pull origin master
git checkout -b release-$ARGUMENTS
```

### 3. Version Management
Set version to target release version:
```bash
hatch version $ARGUMENTS
git commit -am "Version: $(hatch version)"
```

### 4. Changelog Generation
```bash
hatch --env develop run towncrier build --keep --version $(hatch version)
git commit -am "Update changelog for v$(hatch version) release."
```

### 5. Quality Assurance Phase
Push branch and monitor QA workflow:
```bash
# Use -u flag for new branches, omit for existing
git push [-u] origin release-$ARGUMENTS

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

### 6. Release Deployment
**Verify QA passed before proceeding to release tag:**
```bash
git tag -m "Release v$(hatch version): <brief-description>." v$(hatch version)
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

### 7. Post-Release Cleanup
```bash
git rm .auxiliary/data/towncrier/*.rst
git commit -m "Clean up news fragments."
git push origin release-$ARGUMENTS
```

### 8. Master Branch Integration
Cherry-pick release commits back to master:
```bash
git checkout master && git pull origin master
git cherry-pick <changelog-commit-hash>
git cherry-pick <cleanup-commit-hash>
git push origin master
```

### 9. Next Development Cycle (Major/Minor Releases Only)
Set up next development version:
```bash
hatch version minor,alpha
git commit -am "Version: $(hatch version)"
git tag -m "Start development for v$(hatch version | sed 's/a[0-9]*$//')." i$(hatch version | sed 's/a[0-9]*$//')
git push origin master --tags
```

**Note**: Use `git log --oneline` to identify commit hashes for cherry-picking.
