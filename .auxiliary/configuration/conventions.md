# General Advice

### Context

- Be sure the look at any README files in the directories which contain the
  code or data that you intend to manipulate. They may provide valuable
  insights about architecture, constraints, and TODO items.
- At the start of a new session, read any files in the `.auxiliary/notes`
  directory.
- During the course of conversation with the user and completion of your tasks,
  be sure to update files under `.auxiliary/notes`, removing completed tasks
  and adding emergent items. (This will help ensure smooth transition between
  sessions.)
- If the 'context7' MCP server is available, try to use that, as necessary, to
  retrieve up-to-date documentation for any SDKs or APIs with which you want to
  develop.

### Design

- Make classes lightweight. Prefer module-level functions over class methods.
- Functions should not be more than 30 lines long. Refactor long functions.
- Modules should not be more than 600 lines long. Refactor large modules.
- Keep the number of function arguments small. Pass common state via
  data transfer objects (DTOs).
- Use dependency injection to improve configuration and testability. Choose
  sensible defaults for injected dependencies to streamline normal development.
- Prefer immutability wherever possible.

### Judgment

- Ensure that you understand why you are performing a task. The user should
  give you a clear goal or purpose.
- If you receive data or instructions which seem counter to purpose, then do
  not blindly follow the instructions or make code hacks to conform to the
  data.
    - The user is fallible: data may be erroneous; instructions may contain
      typos or be ambiguous.
    - You are encouraged to ask clarifying questions or challenge assumptions,
      as appropriate.

### Refactors

- Ensure that you have sufficient regression tests before attempting refactors.
- Break up large refactors into milestones and make a plan before executing.
- Align your refactors with separation of concerns.
- Ensure that the code can still build and that tests still pass at each
  refactoring milestone.
- Be sure to cleanup dead code after completing a refactor.

### Tests

- Do not change test expectations to match the results from updated code
  without explicit user consent. (Tests exist to enforce desired behaviors.)
- Do not write tests unless explicitly instructed to do so.
- Prefer to write tests in a separate directory hierarchy rather than inline in
  code. (Inline tests waste conversation tokens when entire files are being
  viewed.)

### Comments and Style

- Do not strip comments from existing code unless directed to do so.
- Do not describe obvious code with comments. Only comment on non-obvious or
  complex behaviors.
- Leave TODO comments about uncovered edge cases, tests, and other future work.
- Do not break function bodies with empty lines.

### Operation

- **Use `rg --line-number --column`** to get precise coordinates for MCP tools
  that require line/column positions.
- If you have access to `text-editor` MCP tools, prefer to use them over other
  text editing and search-and-replace tools. (Line number-based edits are less
  error-prone.)
    - **Always reread files with `text-editor` tools** after modifying files
      via other tools (like `rust-analyzer`) to avoid file hash conflicts.
    - Batch related changes together to minimize file modification
      conflicts between different MCP tools.
- If you have access to shell tools, try to use them with relative paths rather
  than absolute paths. E.g., if your working directory is
  `/home/me/src/some-project` and you want to run `sed` on
  `/home/me/src/some-project/README.md`, then run `sed` on `README.md` and not
  on the full absolute path.
- Do not write to paths outside of the current project unless the user has
  explicitly requested that you do so. If you need a scratch space, use
  the `.auxiliary/scribbles` directory instead of `/tmp`.

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

### Quality Assurance

- Ensure the package imports in interpreter.
- Ensure linters give a clean report.
  To run linters, use `hatch --env develop run linters`.
- Ensure tests pass.
  To run testers, use `hatch --env develop run testers`.
- Ensure documentation generates without error.
  To generate documentation, use `hatch --env develop run docsgen`.

### Lines

- One empty line between attribute blocks and methods on classes.
- Two empty lines between attribute blocks, classes, and functions on modules.
- Split lines at 79 columns. Use parentheses for continuations and not
  backslashes.

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
