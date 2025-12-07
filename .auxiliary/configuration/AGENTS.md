# Context

- Project overview and quick start: README.rst
- Product requirements and goals: documentation/prd.rst
- System architecture and design: @documentation/architecture/
- Development practices and style: @.auxiliary/instructions/
- Current session notes and TODOs: @.auxiliary/notes/

- Use the 'context7' MCP server to retrieve up-to-date documentation for any SDKs or APIs.
- Use the 'librovore' MCP server to search structured documentation sites with object inventories (Sphinx-based, compatible MkDocs with mkdocstrings). This bridges curated documentation (context7) and raw scraping (firecrawl).
- Check README files in directories you're working with for insights about architecture, constraints, and TODO items.
- Update files under `.auxiliary/notes` during conversation, removing completed tasks and adding emergent items.

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

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

# Commits

- Use `git status` to ensure all relevant changes are in the changeset.
- Do **not** commit without explicit user approval. Unless the user has requested the commit, **ask first** for a review of your work.
- Use present tense, imperative mood verbs (e.g., "Fix" not "Fixed").
- Write sentences with proper punctuation.
- Include a `Co-Authored-By:` field as the final line. Should include the model name and a no-reply address.

# Project Notes

<!-- This section accumulates project-specific knowledge, constraints, and deviations.
     For structured items, use documentation/architecture/decisions/ and .auxiliary/notes/todo.md -->
