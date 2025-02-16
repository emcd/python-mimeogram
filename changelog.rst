

.. towncrier release notes start

Mimeogram 1.0 (2025-02-14)
==========================

Features
--------

- Add ``mimeogram create`` command for bundling files into clipboard-ready
  documents:

  * Preserves directory structure and file metadata
  * Supports recursive directory traversal
  * Honors Git ignore rules
  * Includes editor integration for adding context messages
  * Provides format instructions for LLMs

- Add ``mimeogram apply`` command for applying changes from mimeograms:

  * Interactive review mode on terminals
  * Hunk-by-hunk selection of changes
  * File content editor integration
  * Protected path detection
  * Atomic file updates

- Add ``mimeogram provide-prompt`` command for setting up LLM projects:

  * Generates format instructions
  * Enables project-level mimeogram support in LLM interfaces
  * Single-command setup for new projects

- Add filesystem protection system to prevent accidental modification of
  sensitive paths

- Add atomic file updates with automatic rollback on errors

- Add Git ignore rule integration to avoid processing unwanted files
