# General Advice

**IMPORTANT:** Read the comprehensive documentation guides:

- **Practices**: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst
- **Style**: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/style.rst
- **Nomenclature**: https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/nomenclature.rst

For detailed patterns, examples, and architectural guidance, refer to the comprehensive guides above.

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

### Essentials

- Avoid namespace pollution - use private aliases and `__` subpackage.
- Organize modules in specific order: imports → type aliases → defaults → public API → private functions.
- Maintain readability with spaces inside of delimiters.
- Maintain readability with vertical compactness of function bodies.
- Prefer immutability wherever possible.
- Use wide abstract types for function parameters (`__.cabc.Sequence`, `__.cabc.Mapping`).
- Return narrow concrete types (`list`, `dict`, `frozenset`, `__.immut.Dictionary`).
- Use narrow try blocks (only risky statements).
- Subclass `Omniexception` or `Omnierror` for package-specific exceptions.

**Example:**

```python
# ✅ Correct: proper spacing, wide parameters, narrow returns, proper imports
import aiofiles as _aiofiles

from . import __

UserData: __.typx.TypeAlias = dict[ str, str | int ]

def process_items(
    items: __.cabc.Sequence[ str ],           # Wide input type
    config: __.cabc.Mapping[ str, int ] = __.immut.Dictionary( )
) -> tuple[ str, ... ]:                      # Narrow return type
    ''' Processes items according to configuration. '''
    return tuple( item.upper( ) for item in items )
```

### Quality Assurance

- Ensure linters give a clean report: `hatch --env develop run linters`
- Address linting issues within the first few conversation turns from when they
  appear.
- Do **not** suppress linter warnings via `noqa` pragma comments without
  explicit user approval.
- Do **not** avoid `TRY003` exceptions from Ruff. Instead, use appropriate
  custom exceptions in the `exceptions` module for the package. If an
  appropriate exception does not exist, then create it.
- Do **not** suppress typechecker warnings via `type` pragma comments without
  explicit user approval. For missing third-party stubs, you can generate them
  with `hatch --env develop run pyright --createstub <import>` and then edit
  the stubs (under `sources/<package>/_typedecls`) to flesh out what you need,
  discarding the remainder.
- Ensure tests pass: `hatch --env develop run testers`
- Ensure documentation generates without error: `hatch --env develop run docsgen`

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
