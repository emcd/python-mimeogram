# Context

- Overview and Quick Start: README.{md,rst}
- Architecture and Design: @documentation/architecture/
- Development Practices: @.auxiliary/instructions/

- Use the 'context7' MCP server to retrieve up-to-date documentation for any SDKs or APIs.
- Use the 'librovore' MCP server to search structured documentation sites with object inventories (Sphinx-based, compatible MkDocs with mkdocstrings). This bridges curated documentation (context7) and raw scraping (firecrawl).
- Use the 'nb' MCP server for project note-taking, issue tracking, and collaboration. The server provides LLM-friendly access to the `nb` note-taking system with proper escaping and project-specific notebook context.
- Check README files in directories you're working with for insights about architecture, constraints, and TODO items.

## Purpose
[Describe your project's purpose and goals]

## Tech Stack
[List your primary technologies]

# Development Standards

Before implementing code changes, consult these files in `.auxiliary/instructions/`:
- `practices.rst` - General development principles (robustness, immutability, exception chaining)
- `practices-python.rst` - Python-specific patterns (module organization, type annotations, wide parameter/narrow return)
- `nomenclature.rst` - Naming conventions for variables, functions, classes, exceptions
- `style.rst` - Code formatting standards (spacing, line length, documentation mood)
- `validation.rst` - Quality assurance requirements (linters, type checkers, tests)

# Operation

- Use `rg --line-number --column` to get precise coordinates for MCP tools that require line/column positions.
- Choose appropriate editing tools based on the task complexity and your familiarity with the tools.
- Use the 'pyright' MCP server where appropriate:
    - `rename_symbol` for refactors
    - `references` for precise symbol analysis
- Batch related changes together when possible to maintain consistency.
- Use relative paths rather than absolute paths when possible.
- Do not write to paths outside the current project unless explicitly requested.
- Use the `.auxiliary/scribbles` directory for scratch space instead of `/tmp`.

## Note-Taking with `nb` MCP Server

### When to Use
- **Project coordination**: Record handoffs, document decisions, maintain task lists.
- **Issue tracking**: Create and manage todos with status tracking.
- **Knowledge sharing**: Document patterns, APIs, and project-specific knowledge.
- **Meeting notes**: Record discussions and action items.

### Scope and Noise Control
- Prefer to update an existing related note/todo over creating a new one when context already exists.
- Avoid logging routine, immediately completed mechanical actions in separate notes.
- Create new notes/todos when information is likely to be useful across sessions or for other collaborators.

### Tagging Conventions (for multi-LLM coordination)
Use consistent tags for discoverability:
- **LLM Collaborator**: `#llm-<name>` (e.g., `#llm-claude`, `#llm-gpt`)
- **Project Component**: `#component-<name>` (e.g., `#component-data-models`)
- **Task Type**: `#task-<type>` (e.g., `#task-design`, `#task-bug`)
- **Status**: `#status-<state>` (e.g., `#status-in-progress`, `#status-review`)
- **Coordination**: `#handoff`, `#coordination`

### Common Patterns
- Check for handoffs: `nb.search` with `#handoff` and `#status-review` tags.
- Find work by specific LLM: `nb.search` with `#llm-<name>` tag.
- Track todos: Use `nb.todo`, `nb.tasks`, `nb.do`, `nb.undo`.
- Organize with folders: `nb.folders`, `nb.mkdir`.

### Recommended `nb` Organization (Project-Defined)
- Prefer a folder taxonomy of `<issue-type>/<component>` (max depth 2) and avoid mixing top-level component folders with top-level issue-type folders.
- Recommended top-level issue types are:
    - `todos/`
    - `handoffs/`
    - `coordination/`
    - `decisions/` (optional for durable rationale notes)
- Example component names include `engine`, `mcp`, `tui`, `web`, `handbook`, and `data-models`.
- This project should define and document its specific component-folder conventions in the **Project Notes** section.
- For cross-component work, prefer `coordination/general` and use multiple `#component-*` tags.
- Keep notebook lifecycle hygiene:
    - prune completed todos quickly,
    - keep only active/near-term handoffs,
    - delete stale history-only notes with no owner or action.

### `nb` vs OpenSpec Rubric
- Use **OpenSpec proposals** for cross-cutting changes, contract-shaping work, architecture shifts, or work that needs explicit design discussion.
- Use **`nb` todos/notes** for scoped, self-contained implementation tasks where the path is straightforward.
- For each active OpenSpec proposal, keep **exactly one** linked `nb` todo as the tracking anchor (with proposal reference), rather than duplicating full task trees in both systems.
- When in doubt, prefer OpenSpec first for design clarity, then track execution updates in the linked `nb` todo.

## OpenSpec Instructions

Workflow Guide: @openspec/AGENTS.md

Always open `openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan).
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work.
- Sounds ambiguous and you need the authoritative spec before coding.

Use `openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

# Commits

- Use `git status` to ensure all relevant changes are in the changeset.
- Do **not** commit without explicit user approval. Unless the user has requested the commit, **ask first** for a review of your work.
- Do **not** bypass commit safety checks (e.g., `--no-verify`, `--no-gpg-sign`) unless the user explicitly approves doing so.
- Use present tense, imperative mood verbs (e.g., "Fix" not "Fixed").
- Write sentences with proper punctuation.
- Include a `Co-Authored-By:` field as the final line. Should include the model name and a no-reply address.
- Avoid using `backticks` in commit messages as shell tools may evaluate them as subshell captures.

# Project Notes

<!-- This section accumulates project-specific knowledge, constraints, and deviations.
     For structured items, use documentation/architecture/decisions/ and `nb`. -->
