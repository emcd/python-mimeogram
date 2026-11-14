## ADDED Requirements

### Requirement: Tri-state boolean flags parse as present/absent

The system SHALL accept exactly three input shapes for tri-state CLI
options: absent, bare `--flag`, and bare `--no-flag`. In scope are the
`DisallowNone[bool | None]` fields (`create`: clip, count_tokens,
recurse, no_ignores, strict, deterministic_boundary; `apply`: clip,
force; `provide-prompt`: clip).

#### Scenario: Omitted flag preserves default tracking
- **WHEN** a boolean flag is absent from the command line
- **THEN** the parsed value is `None`, signaling the config layer to apply.

#### Scenario: Positive flag sets True
- **WHEN** `--flag` is supplied without a value
- **THEN** the parsed value is `True`.

#### Scenario: Negative flag sets False
- **WHEN** `--no-flag` is supplied without a value
- **THEN** the parsed value is `False`.

#### Scenario: Explicit boolean value is rejected
- **WHEN** `--flag True` is supplied as separate arguments
- **THEN** parsing fails with a usage error (exit 2).

#### Scenario: Explicit boolean value with equals is rejected
- **WHEN** `--flag=True` or `--flag=False` is supplied
- **THEN** parsing fails with a usage error (exit 2).

#### Scenario: Help advertises flag pairs
- **WHEN** `--help` renders a tri-state boolean option
- **THEN** it lists the `--flag`/`--no-flag` pair with no value placeholder.

### Requirement: Ordinary boolean defaults are preserved

The system SHALL preserve declared defaults and flag behavior for plain
`bool` CLI options (`create`: edit, prepend_prompt); this revision
changes nothing about them.

#### Scenario: Ordinary bool default holds when omitted
- **WHEN** `--edit` and `--prepend-prompt` are absent from the command line
- **THEN** the parsed values equal their declared defaults (`False`).

#### Scenario: Ordinary bool flag sets True
- **WHEN** `--edit` is supplied without a value
- **THEN** the parsed value is `True`.
