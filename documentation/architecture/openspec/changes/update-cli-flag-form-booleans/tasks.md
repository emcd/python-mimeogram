## 1. Dependency floor

- [ ] 1.1 Add explicit `tyro ~= 1.0.15` to `pyproject.toml` dependencies.
- [ ] 1.2 Re-sync develop environment and re-run linters plus test suite.

## 2. Documentation sweep

- [ ] 2.1 Replace all `--flag=True`/`--flag=False` spellings in
      `documentation/examples/cli.rst` with `--flag`/`--no-flag`.
- [ ] 2.2 Audit `create`, `apply`, and `provide-prompt` help text for any
      promise of explicit boolean values; correct as needed.
- [ ] 2.3 Run docsgen linkcheck to confirm examples still validate.

## 3. Major release

- [ ] 3.1 Add Towncrier fragment for the breaking CLI spelling change.
- [ ] 3.2 Bump `__version__` to `2.0.0`.
- [ ] 3.3 Full validation (linters, testers, CLI smoke test) and commit.

## 4. Parser evidence

- [ ] 4.1 Extend real-parser tests with explicit-value rejection: separate
      (`--flag True`/`--flag False`) and equals (`--flag=True`) forms,
      asserting usage-error exit 2 without dispatching commands.
- [ ] 4.2 Assert `--help` output for representative tri-state flags lists
      the `--flag`/`--no-flag` pair with no value placeholder.
- [ ] 4.3 Assert ordinary bool defaults hold (`edit`, `prepend_prompt`
      default `False`; `--edit` sets `True`).
- [ ] 4.4 Cover representative tri-state flags across all three commands
      (`create`: clip, recurse; `apply`: force; `provide-prompt`: clip),
      verifying each rewritten example alias parses.
- [ ] 4.5 Preserve config inheritance semantics: absent parses to `None`
      and explicit flags override config; no test dispatches application
      commands or touches clipboard/protected files.
