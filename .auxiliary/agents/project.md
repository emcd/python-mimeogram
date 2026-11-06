# Project Guidance

Project-owned knowledge the generated `AGENTS.md` entrypoint must not own.
Structured tracking stays in `nb`.

## Purpose

Mimeogram is a command-line tool for exchange of file collections with large
language models: bundle files into a single clipboard-ready document
preserving directory structure and metadata, then round-trip LLM-proposed
changes back to the filesystem with interactive per-part review and
filesystem protection. Complements agentic tools where explicit, auditable
context selection or provider portability is needed.

## Tech Stack

Python >= 3.12 (CPython 3.12 through 3.15); Hatch build and envs; runtime deps emcd-appcore[cli],
detextive, httpx, rich with CLI via tyro; QA via pytest, pyright, ruff,
isort, sphinx, towncrier, vulture.

## Notes

- Fleet: Coordinator (coordinator@infrastructure); Tier-1 Reviewer General
  (reviewer@infrastructure); Tier-2 Advisor (advisor@infrastructure).
  Bundle neighbor: Librovore Owner (librovore-o@ai-applications).
  Template guidance: Template Owner (template-o@python-foundation).

<!-- Accumulate project-specific knowledge, constraints, deviations, and durable
     links here. For structured items, use `nb`.

     Migration: if upgrading from an AGENTS.md that still had inline Purpose,
     Tech Stack, or Project Notes sections, move that body here once, then accept
     the template-owned AGENTS.md pointer.

     TODO: If this project uses multiple agent/clone roles, create a stable
     team-organization note in `nb`, modeled after one of the examples at:
     https://raw.githubusercontent.com/emcd/agents-common/master/examples/nb-notes/team-organization/README.md
     Then link the note here, for example:
     - Team org, role ownership, signoff policy, and merge workflow: `coordination/general/<n>` -->
