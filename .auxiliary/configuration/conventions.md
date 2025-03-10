# General Advice

### Design

- Make classes lightweight. Prefer module-level functions over class methods.
- Functions should not be more than 30 lines long. Refactor long functions.
- Keep the number of function arguments small. Pass common state via
  lightweight data transfer objects (DTOs).
- Use dependency injection to improve configuration and testing. Choose
  sensible defaults for injected dependencies to streamline normal development.
- Prefer immutability wherever possible.

# Per-Language Advice

## Python

### Design and Idioms

- Target Python 3.10 and use idioms appropriate for that version
  (`match`..`case`, type unions via `|`, etc...).
- Do not pollute the module namespace with public imports. Either import inside
  of functions or else alias module-level imports as private, depending on how
  imports affect performance.
- Take note of the internal `__` subpackage, which exposes imports used
  internally throughout the package (`cabc` alias for `collections.abc`,
  `enum`, `types`, `typx` alias for `typing_extensions`, etc...).
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
- Two empty lines between attribute blocks and functions on modules.
- Split lines at 79 columns. Use parentheses for continuations and not
  backslash.
