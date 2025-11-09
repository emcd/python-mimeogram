# Known Issues

## CLI Parser Failure with tyro

**Discovered**: 2025-11-09 during Detextive 2.0 port verification

**Status**: Pre-existing issue (exists before Detextive 2.0 port)

**Severity**: Critical - CLI is completely non-functional

### Description

The mimeogram CLI fails to start with a tyro parser error:

```
AssertionError: UnsupportedStructTypeMessage(message="Empty hints for <slot wrapper '__init__' of '_io.TextIOWrapper' objects>!")
```

### Reproduction

```bash
hatch run mimeogram --help
# or any other command: version, create, apply, provide-prompt
```

### Analysis

The error originates from `tyro` attempting to parse the CLI structure and encountering a type that lacks proper type hints. The error occurs in:

```
File "/root/.local/share/hatch/env/.../tyro/_parsers.py", line 113, in from_callable_or_type
    assert not isinstance(out, UnsupportedStructTypeMessage), out
```

The error mentions `_io.TextIOWrapper`, suggesting that somewhere in the command classes or their dependencies, there's a reference to stdin/stdout/stderr or file handles that tyro cannot introspect.

### Timeline

- **Commit 556db71** (Merge PR #9 - appcore cutover): Error present
- **Commit fac1d9f** (Integrate detextive package): Error present
- **Commit c1401a1** (Port to Detextive 2.0): Error present
- **Commit 32a777f** (Fix linter errors): Error present

This indicates the issue was introduced during the appcore refactor (PR #9), not by the Detextive 2.0 port.

### Investigation Points

1. **appcore type annotations**: The issue likely stems from how `appcore` types are exposed to tyro
2. **CLI command definitions**: Check `cli.py`, `create.py`, `apply.py`, `prompt.py` for problematic type hints
3. **TextIOWrapper references**: Search for uses of `sys.stdin`, `sys.stdout`, `sys.stderr` that may need explicit typing

Confirmed uses in codebase:
- `sources/mimeogram/apply.py:134`: `__.sys.stdin.isatty()`
- `sources/mimeogram/apply.py:144`: `__.sys.stdin.read()`
- `sources/mimeogram/interactions.py:76`: `__.sys.stdout.flush()`
- `sources/mimeogram/display.py:60`: `__.sys.stdin.isatty()`

### Suggested Fix

Based on the user's suggestion: Switch to `emcd-appcore[cli]` which likely includes additional dependencies or type stubs that help tyro properly parse the CLI structure.

### Impact

- **Tests**: All 173 tests pass (tests don't exercise CLI parsing, they import modules directly)
- **Linters**: Pass cleanly (ruff and pyright)
- **Detextive integration**: Working correctly
- **CLI functionality**: Completely broken - cannot run any commands

### Workaround

None currently available. The application can be used programmatically by importing modules directly, but the CLI is unusable.

### Next Steps

1. Try switching dependency from `emcd-appcore~=1.4` to `emcd-appcore[cli]~=1.4`
2. If that doesn't resolve it, investigate the specific type annotation that tyro cannot parse
3. Consider adding explicit type annotations to any stdin/stdout/stderr usage
4. May need to report issue to `tyro` if it's a limitation in their type introspection
