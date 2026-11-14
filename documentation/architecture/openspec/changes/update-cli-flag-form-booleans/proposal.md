## Why

Tyro 1.x renders `DisallowNone[bool | None]` fields as `--flag`/`--no-flag`
pairs and rejects explicit `--flag <boolean>` values (verified on 1.0.15
through 1.0.17, matching the `emcd-appcore[cli]` floor of `tyro ~= 1.0.15`).
The documented examples still teach the old `--flag=True` spelling, which now
exits 2. Aligning docs, declaring the explicit Tyro floor, and releasing a
major version closes the CLI revision tracked for this project.

## What Changes

- Add explicit `tyro ~= 1.0.15` dependency to `pyproject.toml` (verified
  minimum for the flag-pair behavior; mirrors the appcore floor).
- **BREAKING**: Remove all `--flag=True`/`--flag=False` spellings from
  `documentation/examples/cli.rst`; replace with `--flag`/`--no-flag`.
- Audit command help text for any promise of explicit boolean values.
- Bump package version to 2.0.0 with a Towncrier fragment.
- Tri-state scope is the existing `DisallowNone[bool | None]` fields only
  (`create`: clip, count_tokens, recurse, no_ignores, strict,
  deterministic_boundary; `apply`: clip, force; `provide-prompt`: clip).
  Plain `bool` fields (`create`: edit, prepend_prompt) keep their declared
  defaults and are explicitly out of scope: no conversion requested.
- No code changes required: absent still parses to `None` (config-file
  layering preserved) for tri-state fields.

## Capabilities

### New Capabilities

- `cli-boolean-flags`: CLI boolean flags parse as present/absent tri-state.

### Modified Capabilities

- None (no existing specs; `openspec/specs/` is empty).

## Impact

- Affected files: `pyproject.toml`, `documentation/examples/cli.rst`,
  `sources/mimeogram/__init__.py` (version), Towncrier fragment.
- Affected users: anyone scripting `--flag <boolean>` spellings (now exit 2).
- Dependencies: new explicit `tyro` floor; behavior otherwise unchanged.
- The `test_450_create_deterministic_boundary_parser` regression test
  (real Tyro parser, None/True/False/help) covers the tri-state core;
  additional parser tests (explicit-value rejection, help output, ordinary
  bool defaults, cross-command representative flags) are tracked as tasks.
