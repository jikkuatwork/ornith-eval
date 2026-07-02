# Agent Instructions

This repo uses the koder pattern for durable agent handoff and project memory.

## Operator layout

- Keep durable non-code agent/operator files under `koder/`.
- Root `AGENTS.md`, `CLAUDE.md`, `.pi/skills/*`, `.claude/skills/*`, and `.agents/skills/*` should be symlinks/adapters to files under `koder/` when possible.
- `README.md` is the root documentation exception because repository hosts render it directly; prefer other durable docs under `koder/docs/` unless project conventions require otherwise.
- Do not put product source code under `koder/` unless the project explicitly says so.

## Session handoff

- Use the `open` skill at the start of a session.
- Use the `close` skill at the end of a session; it updates `koder/STATE.md` and creates a grepable `state: close - ...` commit for the semantic state transition.
- Read `koder/STATE.md` before making changes when opening manually.
- Keep `koder/STATE.md` short and current; update it at init, close, explicit handoff requests, or external-origin filings into this repo.
- Do not put secrets, private payloads, full prompts, credentials, or large copied source/output into `koder/`.

## State commits

- Every intentional `koder/` state transition gets a `state:` commit by default.
- Use subjects like `state: init - koder pattern scaffold`, `state: close - <result>`, `state: file #NNN from <origin> - <reason>`, or `state: update #NNN - <reason>`.
- `state:` commits are the semantic movement ledger; `koder/STATE.md` is the session handoff, not a commit-by-commit changelog.
- Do not edit `koder/STATE.md` solely because a local in-session artifact state commit happened; summarize at close if it matters.
- Do not force ordinary code-only commits to use `state:`; the ledger tracks semantic operator/repo-state movement.
- In dirty repos, commit only the intended state paths and preserve unrelated dirty/staged work.
- If the user explicitly says not to commit, leave state uncommitted and report the dirty paths.

## Koder artifacts

- Minimum scaffold: `koder/STATE.md`, `koder/issues/`, `koder/skills/open/`, and `koder/skills/close/`.
- Create other artifact directories only when needed, for example `koder/proposals/`, `koder/plans/`, `koder/reviews/`, `koder/research/`, `koder/analysis/`, `koder/notes/`, `koder/tasks/`, `koder/queues/`, or `koder/scratch/`.
- Use folder-first artifacts for durable records: `koder/<type>/NNN_short_slug/INDEX.md`.
- Use `koder/proposals/` for RFC-scale ideas that should converge before issues/plans are extracted.
- Treat `INDEX.md` as canonical current state; use `turns/` only for optional discussion/history.
- Scan existing artifacts before choosing the next number; each artifact type has its own sequence.
- Prefer source links, file paths, command names, commits, and concise evidence over copied detail.
- Run local validators before finalizing artifacts when validators exist.

## Safety

- Never commit secrets, credentials, private account identifiers, sensitive personal data, private payloads, full prompts, or large generated outputs.
- Ask before running commands that deploy, create cloud resources, mutate production data, install packages globally, rotate credentials, or change account/member access.
- Preserve live project conventions; these instructions are the operator baseline, not a replacement for project-specific policy.
