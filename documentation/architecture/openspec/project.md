# Project Context

## Purpose
This is a command-line tool for **exchanging collections of files with Large Language Models (LLMs)**. It bundles multiple files into a single clipboard-ready document while preserving directory structure and metadata, making it ideal for code reviews, project sharing, and LLM interactions. It supports interactive reviews, clipboard integration, and path protection.

## Tech Stack
- **Language**: Python 3.10+
- **Build System**: Hatch
- **Packaging**: PyInstaller (for standalone executable)
- **Key Libraries**:
  - `accretive` (accretive data structures)
  - `aiofiles` (async file I/O)
  - `detextive` (text detection)
  - `httpx` (HTTP client)
  - `icecream-truck` (debugging)
  - `patiencediff` (diff generation)
  - `pyperclip` (clipboard integration)
  - `rich` (terminal formatting)
  - `tiktoken` (token counting)
  - `tomli` (TOML parsing)
  - `tyro` (CLI argument parsing)
  - `appcore` (application core utilities)

## Project Conventions

### Code Style
- **Line Length**: 79 characters
- **Indentation**: 4 spaces
- **Type Hinting**: Strict type checking with `pyright` (reportUnknownArgumentType, etc. are true).
- **Linters**:
  - `ruff` (general linting)
  - `isort` (import sorting)
- **Configuration**: See `pyproject.toml` for detailed linter configurations.

### Architecture Patterns
- **Filesystem Organization**: See [`documentation/architecture/filesystem.rst`](../filesystem.rst) for details on the project structure.
- **Import Hub Pattern**: Uses a centralized `__` import hub (e.g., `from . import __`) to manage internal and external dependencies.
- **CLI Separation**: The CLI logic is separated into `cli.py` and `__main__.py` to allow independent testing and execution.
- **Immutability**: Uses `frigid` and `accretive` for immutable and append-only data structures where appropriate.

### Testing Strategy
- **Framework**: `pytest`
- **Property-based Testing**: `hypothesis`
- **Coverage**: Branch coverage enabled, enforced via CI.
- **Doctests**: Run via Sphinx.
- **Test Naming**: `test_[0-9][0-9][0-9]_*` pattern for test functions.
- **Location**: All tests are located in the `tests/` directory.

### Git Workflow
- **Branching**: Pull Request (PR) based workflow.
- **Changelog**: Managed via `towncrier`. Changelog fragments are stored in `.auxiliary/data/towncrier` and compiled into `documentation/changelog.rst`.
- **CI/CD**: GitHub Actions for testing and linting.

## Domain Context
- **LLM Context Windows**: The tool is designed to optimize for limited context windows of LLMs.
- **Mimeogram Format**: A specific textual format for bundling files that LLMs can understand and generate.
- **Clipboard Operations**: Heavy reliance on system clipboard for data transfer between the tool and LLM interfaces (web/desktop).
- **Path Protection**: Security mechanism to prevent LLMs from modifying sensitive files or directories.

## Important Constraints
- **Platform Support**: Must work on Linux, macOS, and Windows.
- **Python Support**: Supports Python 3.10 to 3.14.
- **No Automatic Sync**: The tool does not automatically sync files; it relies on manual `create` and `apply` steps.

## External Dependencies
- **LLM Providers**: Interacts with LLMs (OpenAI, Anthropic, etc.) indirectly via text/clipboard.
- **GitHub**: Supports fetching files from remote GitHub URLs.
