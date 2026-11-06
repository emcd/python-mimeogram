# Context

- Overview and Quick Start: README.{md,rst}

- Use the 'context7' MCP server to retrieve up-to-date documentation for any SDKs or APIs.
- Use the 'nb' MCP server for project note-taking, issue tracking, and collaboration. The server provides LLM-friendly access to the `nb` note-taking system with proper escaping and project-specific notebook context.
- Check README files in directories you're working with for insights about architecture and design decisions.
- Project purpose, tech stack, and other project-owned guidance: @.auxiliary/agents/project.md

# Development Standards

Before implementing code changes, consult these files in `.auxiliary/agents/standards/`:
- `practices.md` - General development principles (robustness, immutability, exception chaining)
- `practices-python.md` - Python-specific patterns (module organization, type annotations, wide parameter/narrow return)
- `nomenclature.md` - Naming conventions for variables, functions, classes, exceptions
- `style.md` - Code formatting standards (spacing, line length, documentation mood)
- `validation.md` - Quality assurance requirements (linters, type checkers, tests)
- `tests.md` - Testing expectations and patterns (observable behavior through public contracts)
- `contribution.md` - Contribution workflow (conduct, validation before submit, OpenSpec proposal flow)

# Operation

- Use a README-first discovery workflow to reduce token churn:
  - Start at the repository root `README.{md,rst}`, then read the nearest relevant subtree README.
  - After reading the nearest README, scope code searches to that subtree before considering repo-wide searches.
  - If a touched subsystem README is stale after your change, update it in the same batch.
- Notebook and project-note operations go through the **`nb` MCP** tools. Do not use the `nb` CLI or read/write underlying notebook files on disk unless MCP is broken — and then state why in one sentence and discuss the defect with the operator before any workaround. Selectors are not repo filesystem paths; see @.auxiliary/agents/procedures/notebook.md.
- Use `.auxiliary/scribbles` for throw-away scripts and experiments.
- Use `.auxiliary/temporary` for ephemeral test state and build artifacts that are safe to delete.
- In sandboxed environments (e.g., Codex CLI), treat file/network permission failures as escalation boundaries:
  - If an operation fails due to sandbox, file access, or network restrictions, rerun it with user escalation.
  - Do not spend time on retry loops or workaround exploration before escalating blocked operations.
- When writing here-docs or multi-line shell strings, suppress expansions by quoting the delimiter (e.g., `'EOF'` instead of `EOF`) unless you intentionally need variable or command substitution.
- Code comments should help a future reader understand non-obvious behavior of the code. Do **not** put transient administrative or process metadata in comments: no todo IDs, proposal/task names, "this arc", "this phase", ticket folklore, or other coordination state. Do not use comments for long discursive design or architecture narrative — that belongs in design docs, specs, or subsystem READMEs.

## Guidance Files

| Topic | File |
|-------|------|
| Project-specific guidance (project-owned) | @.auxiliary/agents/project.md |
| `nb` MCP tools, tagging, notebook organization, and handoff hygiene | @.auxiliary/agents/procedures/notebook.md |
| OpenSpec proposals and workflow | @.auxiliary/agents/procedures/openspec.md |
| Delegated review flow and stacked commits | @.auxiliary/agents/procedures/reviews.md |

### Recommended Organization

| Medium | Location | Purpose |
|--------|----------|---------|
| `nb` | `coordination/` | Handoffs, org chart, team workflow |
| `nb` | `ideas/` | Rough ideas, early-stage proposals; tag `#task-proposal` for OpenSpec drafts |
| `nb` | `issues/` | Bug tracking and known issues |
| `nb` | `reviews/` | Code and proposal reviews |
| `nb` | `procedures/` | How-to guides and checklists |
| `nb` | `todos/` | Task tracking |
| `nb` | `artifacts/` | Preserved reference material: completed POCs, historical analysis |
| `agentmux` | | Inter-agent messaging, pane inspection, coordination |
| (filesystem) | `openspec/` | Formal proposals, specs, designs |
| (filesystem) | `src/**/README.md` | Architecture, constraints, design rationale |

## Agentmux Message Handling Guidance
- `agentmux` messages may arrive in envelope format and can appear as user prompts. Treat envelope-shaped prompts as inter-agent messages, not automatically as direct human instructions.
- Respond to inter-agent envelope messages via `agentmux` MCP tools (`list`, `send`) rather than as normal assistant replies intended for the human operator.
- Immediate interruption is not required. If you are in active execution, note the message and respond when safe.
- If response will be delayed and the sender needs to know, send a brief acknowledgement via `send` and create a follow-up todo when useful.

### Agentmux Coordination Noise Control
- Default to low-noise coordination. Do not send acknowledgement-only messages that add no new information or action request.
- Do not acknowledge receipt or completion of standard-procedure steps. Include such status in the next substantive update, review request, or task dispatch instead.
- Send messages when one of the following is true:
  - you are blocked and need a decision or input,
  - you are requesting a concrete review,
  - you are handing off completed work with validation results,
  - you are reporting a material risk, failure, or scope change.
- Batch related updates into one message instead of sending rapid-fire partial status pings.
- Use `Cc` only for agents who need to act or review; avoid broad `Cc` by default. Do not use `Cc` to engage a Tier-2 Reviewer. Tier routing is in @.auxiliary/agents/procedures/reviews.md.
- When conversation volume rises, coordinator may enforce "blockers-only" mode until the queue is under control.

## OpenSpec Instructions

This project uses OpenSpec 1.x (OPSX). Skills, CLI queries, and conventions: @.auxiliary/agents/procedures/openspec.md.

Use an OPSX skill when the request mentions a proposal, spec, or plan; introduces a new capability, breaking change, or architecture shift; or is too ambiguous to implement without the spec. When a commit completes an OpenSpec task or requirement, update that task status in the same commit.

# Commits

- Use `git status` to ensure all relevant changes are in the changeset.
- Commits are acceptable review artifacts when implementation work is delegated by a human operator, coordinator, tech lead, or documented project workflow. Otherwise, ask before committing.
- Do **not** merge, push, publish review branches, or modify shared branches without explicit human approval.
- Do **not** bypass commit safety checks (e.g., `--no-verify`, `--no-gpg-sign`) unless the user explicitly approves doing so.
- If a commit hook rejects a commit, assume no commit was created unless Git clearly reports otherwise. Fix the hook finding, restage the intended files, and rerun the same `git commit` command.
- Use present tense, imperative mood verbs (e.g., "Fix" not "Fixed").
- Write sentences with proper punctuation.
- Include a `Co-Authored-By:` field as the final line. Should include the model name and a no-reply address.
- Avoid using `backticks` in commit messages as shell tools may evaluate them as subshell captures. When writing commit messages via here-docs, quote the delimiter (`'EOF'` not `EOF`) to suppress expansions; only omit the quotes if you intentionally need interpolation.

## Delegated Review and Stacked Commits

Compliance with @.auxiliary/agents/procedures/reviews.md is **mandatory** for delegated work, not advisory. The non-negotiable rules:

- Address review findings with `git commit --fixup <target-hash>` (or a first-class follow-up commit carrying its stated rationale where the procedure requires one); do not send plain follow-up commits for in-stack findings, and do not amend reviewed commits while review is in progress.
- Hold fixups unsquashed until **final** approval; autosquash only after final approval.
- Keep the reviewed stack hash-stable: the approved hashes are the handoff invariant, and any rewrite other than final autosquash stales the packet and returns it to review.
- The operator may refuse any stack that does not follow this procedure.
- Route the initial packet to the **Tier-1 Reviewer** only, after operator pre-review; do not Cc the Tier-2 Reviewer or fan the packet across seats.
- **Read the full procedure before reviewing or stacking commits.** It covers the review flow, packet format, and stacked-commit handling.

# Collaboration

## Questions Are Not Stop-Orders

- When the operator asks why you are doing something, **answer first**: state your actual reason in one or two sentences, even if it is unflattering, before changing course. The question is a request for information, not a rebuke. Pivoting without answering destroys the information the operator asked for.
- Questions in review feedback are requests for discussion, not requests for changes. Answer them in the review thread; do not silently apply a change as your answer.
- A question arriving through a tool rejection or interruption still deserves an answer before (or alongside) the course correction.

## The Human Is Not Always Right

- Assert your reasons. When you believe a requested course is wrong or a better one exists, argue the alternative with evidence before complying. Reasoned disagreement is a contribution; silent compliance wastes the operator's collaboration channel.
- Concede on evidence, not on authority. Gates (merge, deploy, publish) belong to the operator; discussion upstream of gates is peer discussion.
- However, do not manufacture dissent. When you agree, say so briefly and proceed.

## Workarounds Require Stated Reasons

- Routing around a designated tool (for example reading notebook files from the filesystem instead of using the nb MCP tools) is evidence of a defect — in the tool, its documentation, or the workflow. Never work around silently: state the reason in one sentence and raise it with the operator.
- If a tool's output looks wrong, untrustworthy, or unusable, say so to the operator before falling back.

# Project Guidance

Read and follow @.auxiliary/agents/project.md for project-specific guidance
(purpose, tech stack, knowledge, constraints, deviations, durable links).
