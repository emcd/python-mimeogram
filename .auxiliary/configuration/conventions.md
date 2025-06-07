# General Advice

### Design

- Make classes lightweight. Prefer module-level functions over class methods.
- Functions should not be more than 30 lines long. Refactor long functions.
- Keep the number of function arguments small. Pass common state via
  data transfer objects (DTOs).
- Use dependency injection to improve configuration and testability. Choose
  sensible defaults for injected dependencies to streamline normal development.
- Prefer immutability wherever possible.

# Per-Language Advice

## Python

### Design and Idioms

- Target Python 3.10 and use idioms appropriate for that version
  (`match`..`case`, type unions via `|`, etc...).
- Note the internal `__` subpackage which exposes imports used internally
  throughout the package (`cabc` alias for `collections.abc`, `enum`, `types`,
  `typx` alias for `typing_extensions`, etc...).
- Do not pollute the module namespace with public imports. Either reference
  common imports from the `__` subpackage or alias module-level imports as
  private.
- Do not use `__all__` to advertise the public API of a module. Name anything,
  which should not be part of this API, with a private name starting with `_`.
- Do not conflate optional arguments (`__.Absential`/`__.absent`) with nullable
  values (`__.typx.Optional`/`None`).
- Prefer custom exceptions, derived from the package base exception,
  `Omniexception`, rather than standard Python exceptions with long custom
  messages.

### Documentation and Annotations

- Pad inside of delimiter pairs with spaces. E.g., `( foo )` and not `(foo)`.
  Except in f-strings and `str.format` inputs.
- Pad binary operators with spaces. E.g., `foo = 42` and not `foo=42`, `1 + 1`
  and not `1+1`, `[ 1 : -n ]` and not `[1:-n]`.
- Docstrings look like `''' Space-padded headline inside of triple-single
  quotes. '''` and not `"""Double quotes and no spaces are hard to read."""`.
- Use double-quoted strings for f-strings, `str.format` templates, and log
  messages. Otherwise, use single-quoted strings.
- Add type hints for arguments, attributes, and return values.
- Do not write "param spam" documentation which states the obvious. Only
  document non-obvious or complex behaviors on arguments and attributes.
- Use PEP 593 `Annotated` with PEP 727 `Doc` for argument, attribute, and
  return value documentation, when necessary.
- Use `TypeAlias` aliases to reuse complex annotations or expose them as part
  of the public API.

### Comments and Lines

- Do not strip comments from existing code unless directed to do so.
- Do not describe obvious code with comments. Only comment on non-obvious or
  complex behaviors.
- Leave TODO comments about uncovered edge cases, tests, and other future work.
- Do not break function bodies with empty lines.
- One empty line between attribute blocks and methods on classes.
- Two empty lines between attribute blocks, classes, and functions on modules.
- Split lines at 79 columns. Use parentheses for continuations and not
  backslashes.

### Lints and Tests

- Check your work by linting, ensuring that the package imports, running tests,
  and generating documentation.
- Ignore any warnings, unless instructed otherwise. Focus only on errors and
  failures.
- To run linters, use `hatch --env develop run linters`.
- To run testers, use `hatch --env develop run testers`.
- To generate documentation, use `hatch --env develop run docsgen`.
- Do not write tests unless explicitly instructed to do so.

# Commits

- Use `git status` to ensure that all relevant changes are in the changeset to
  be committed.
- Look at the previous five commit messages for guidance on message style.
- Use present tense, imperative mood verbs to describe changes. E.g. "Fix" and
  *not* "Fixed".
- The commit message should include a `Co-Authored-By:` field as its final
  line. The name of the author should be your model name. The email address
  should either be one which you have been designated to use or else a
  commonly-known no-reply address.

## Interactive Collaboration on User Terminal

- Do not commit until you have user approval to do so.
- Add the `--no-gpg-sign` option to the `git commit` command to suppress GPG
  passphrase challenges. (These challenges conflict with the alternate console
  screen, managed by some CLI agents, resulting in an unusable terminal.)
