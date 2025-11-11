# Known Issues

## CLI Clipboard Integration in Non-TTY Environments

**Status:** Open
**Severity:** Minor
**Discovered:** 2025-11-10

Commands that use clipboard operations (create with default clipboard behavior, provide-prompt) appear to hang in non-TTY environments even though they complete successfully. The process doesn't exit cleanly after clipboard copy.

**Workaround:** Use `--clipboard False` flag for create command when running in non-TTY environments.

**Example:**
```bash
# Hangs in non-TTY:
hatch run mimeogram create file.txt

# Works fine:
hatch run mimeogram create --clipboard False file.txt
```

## Directory Recursion with --recurse Flag

**Status:** Resolved (2025-11-10)
**Severity:** Minor
**Discovered:** 2025-11-10
**Resolution:** Added `--no-ignores` CLI flag to disable gitignore filtering, with warnings when files are filtered

Passing a directory path directly with `--recurse True` previously failed with "MimeogramFormatEmpty" error when the directory or its contents were gitignored.

**Root Cause:** Gitignore filtering was applied to all paths. When directories like `.auxiliary/scribbles/` contain `.gitignore` files with `*` patterns, all files were filtered out, resulting in empty mimeograms.

**Fix:** Added `--no-ignores` flag to disable gitignore filtering. Default behavior maintains backward compatibility (gitignore filtering enabled). When files are filtered, warnings are emitted to guide users to use `--no-ignores` if desired.

**Examples:**
```bash
# Default behavior - respects gitignore, shows warnings:
hatch run mimeogram create --recurse True .auxiliary/scribbles/mydir/
# WARNING: Skipping path (matched by .gitignore): ... Use --no-ignores to include.

# With --no-ignores flag - includes all files:
hatch run mimeogram create --recurse True --no-ignores True .auxiliary/scribbles/mydir/
```

## Token Counting Error Message for Missing API Key

**Status:** Open
**Severity:** Minor - Enhancement Opportunity
**Discovered:** 2025-11-10

When using `--tokenizer anthropic-api` without a configured API key, the error message "Could not count mimeogram tokens." is not specific enough to indicate the root cause.

**Suggestion:** Improve error message to indicate missing API key configuration.

**Example:**
```bash
# Current behavior - generic error:
hatch run mimeogram create --count-tokens True --tokenizer anthropic-api file.txt
# ERROR: Could not count mimeogram tokens.

# Suggested improvement:
# ERROR: Could not count mimeogram tokens. Anthropic API tokenizer requires ANTHROPIC_API_KEY environment variable.
```

**Note:** The tiktoken tokenizer works correctly as an alternative.
