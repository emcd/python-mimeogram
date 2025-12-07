# Opencode Plugins for Quality Assurance

This directory contains Opencode plugins that provide quality assurance and development workflow enforcement, ported from Claude Code hooks.

## Plugins

### ✅ 1. `post-edit-linter.js` (WORKING)
**Purpose**: Runs linters after file updates  
**Event**: `tool.execute.after` (for `edit` tool)  
**Behavior**: 
- Checks if `hatch` command is available
- Checks if `develop` Hatch environment exists
- Runs `hatch --env develop run linters`
- Throws error with truncated output (50 lines max) if linters fail
- Early exit if conditions not met (hatch not available)
- **Note**: Uses `tool.execute.after` not `file.edited` (LLM-initiated edits don't trigger `file.edited`)

### ⚠️ 2. `git-commit-guard.js-disabled` (DISABLED - Opencode bash tool limitation)
**Purpose**: Would prevent git commits when linters or tests fail  
**Status**: **DISABLED** - Opencode's bash tool doesn't pass command in `input.args.command`
**Issue**: Plugin intercepts `tool.execute.before` but `input.args` is empty for bash tool
**Original intent**: Port of Claude Code hook `pre-bash-git-commit-check`

### ⚠️ 3. `python-environment-guard.js-disabled` (DISABLED - Opencode bash tool limitation)
**Purpose**: Would detect improper Python usage in Bash commands  
**Status**: **DISABLED** - Opencode's bash tool doesn't pass command in `input.args.command`
**Issue**: Plugin intercepts `tool.execute.before` but `input.args` is empty for bash tool
**Original intent**: Port of Claude Code hook `pre-bash-python-check`

## Installation for Downstream Projects

When this template is copied to a downstream project:

1. **Navigate to the plugin directory**:
   ```bash
   cd .auxiliary/configuration/coders/opencode/plugin
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Ensure symlink exists**:
   ```bash
   # From project root
   ln -sf .auxiliary/configuration/coders/opencode .opencode
   ```

4. **Verify plugin loading**:
   Opencode should automatically load plugins from `.opencode/plugin/`

## Dependencies

- `shlex`: Shell command parsing (port of Python's shlex module) - used in disabled plugins
- `bun`: Runtime (provided by Opencode)

## Porting Notes

These plugins are ports of Claude Code hooks with varying success:

| Claude Code Hook | Opencode Plugin | Status | Key Changes |
|-----------------|----------------|--------|-------------|
| `post-edit-linter` | `post-edit-linter.js` | ✅ **WORKING** | Python → JavaScript, `subprocess` → Bun shell API, uses `tool.execute.after` not `file.edited` |
| `pre-bash-git-commit-check` | `git-commit-guard.js-disabled` | ⚠️ **DISABLED** | Tool name: `Bash` → `bash`, uses npm `shlex` package. **Issue**: Opencode bash tool doesn't pass command in `input.args.command` |
| `pre-bash-python-check` | `python-environment-guard.js-disabled` | ⚠️ **DISABLED** | Same parsing logic with `shlex`, exact error messages. **Issue**: Opencode bash tool doesn't pass command in `input.args.command` |

## Critical Discovery

**Opencode's bash tool limitation**: During testing, we discovered that Opencode's bash tool doesn't pass the command string in `input.args.command` (or any `input.args` field). The `input.args` object is empty `{}` when the bash tool is invoked. This prevents plugins from intercepting and analyzing bash commands.

**Working solution**: Only `post-edit-linter.js` works because it uses `tool.execute.after` for the `edit` tool, where file information is available in `output.metadata.filediff.file`.

## Error Messages

All error messages match the original Claude Code hooks exactly, including:
- Linter output truncation to 50 lines
- "Divine admonition" for git commit blocking
- Warning messages for Python usage

## Testing

To test the plugins:

1. **File edit test**: Edit a Python file and verify linters run
2. **Git commit test**: Try `git commit -m "test"` and verify checks run
3. **Python usage test**: Try `python -c "print('test')"` and verify warning

## Troubleshooting

**Plugins not loading**:
- Verify `.opencode` symlink points to `.auxiliary/configuration/coders/opencode`
- Check Opencode version supports plugin API
- Ensure dependencies are installed (`npm install`)

**Command not found errors**:
- Verify `hatch` is installed and in PATH
- Check `develop` Hatch environment exists: `hatch env show`

**Timeout issues**:
- Timeouts match Python hooks (60s, 120s, 300s)
- Uses `Promise.race` with `setTimeout` since Bun shell lacks native timeout

## Source Code

Original Claude Code hooks in `template/.auxiliary/configuration/coders/claude/scripts/`:
- `post-edit-linter`
- `pre-bash-git-commit-check`  
- `pre-bash-python-check`