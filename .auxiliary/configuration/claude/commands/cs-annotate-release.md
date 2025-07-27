---
allowed-tools: Bash(git log:*), Bash(git show:*), Bash(ls:*), Bash(grep:*), Grep, Read, Write, LS
description: Create Towncrier news fragments for user-facing changes since last release cleanup
---

# Write Release Notes

**NOTE: This is an experimental workflow! If anything seems unclear or missing,
please stop for consultation with the user.**

You are tasked with creating Towncrier news fragments for user-facing changes
since the last release cleanup. This command analyzes recent commits and
generates appropriate changelog entries.

Special instructions: `$ARGUMENTS`
(If above line is empty, then no special instructions were given by the user.)

## Context

The project uses Towncrier to manage changelogs. News fragments are stored in
`.auxiliary/data/towncrier/` and follow specific naming and formatting
conventions detailed in the [releases
guide](https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/releases.rst).

## Process

### Phase 1: Discovery and Analysis

1. **Find Starting Point**: Use `git log --oneline --grep="Clean up news fragments"` to find the last cleanup commit
2. **Get Recent Commits**: Retrieve all commits since the cleanup using `git log --no-merges` with full commit messages
3. **Check Existing Fragments**: List existing fragments in `.auxiliary/data/towncrier/` to avoid duplication

### Phase 2: Filtering and Classification

4. **Filter User-Facing Changes**: Focus on changes that affect how users interact with the tool:
   - CLI command changes (new options, arguments, output formats)
   - API changes (public functions, classes, return values)
   - Behavior changes (different responses, error messages, processing)
   - Configuration changes (new settings, file formats)
   - Deprecations and removals
   - Platform support changes (Python versions, OS support)

   **Exclude** internal changes:
   - GitHub workflows
   - Dependency changes without API impact
   - Internal module restructuring that preserves public API
   - Git ignore files
   - Modules in internals subpackages (`__`)
   - Version bumps and maintenance updates
   - Internal refactoring without user-visible changes

   **Key Test**: Ask "Does this change how a user invokes the tool, what options they have, or what behavior they observe?"

5. **Classify Changes**: Determine appropriate type for each change:
   - `enhance`: features and improvements
   - `notify`: deprecations and notices
   - `remove`: removals of features or support
   - `repair`: bug fixes

   Note: Some commits may contain multiple types of changes.

### Phase 3: Synthesis and Creation

6. **Group Related Commits**: Synthesize multiple commits into coherent user-facing descriptions when they represent logical units of change

7. **Think Through Fragments**: Before writing, consider:
   - Are the descriptions clear and meaningful to users?
   - Do they follow the format guidelines?
   - Are they properly classified?
   - Do they focus on what and why, not how?

8. **Create Fragments**: Write appropriately named fragment files using:
   - `<issue_number>.<type>.rst` for changes with GitHub issues
   - `+<title>.<type>.rst` for changes without issues

   Fragment content should:
   - Start with capital letter, end with period
   - Use present tense imperative verbs
   - Be understandable by users, not just developers
   - Include topic prefixes when appropriate (e.g., "CLI: ", "API: ")

### Phase 4: Final Review and Commit

9. **Summary**: Provide a brief summary of fragments created and any notable patterns or changes identified

10. **Commit Changes**: Add fragments to git and commit them:
    - `git add .auxiliary/data/towncrier`
    - `git commit -m "Add news fragments for upcoming release"`

## Additional Instructions

- Read full commit messages for context; only examine diff summaries if commit messages are unclear
- Focus on meaningful user-facing changes rather than comprehensive coverage of all commits
