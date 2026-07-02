---
name: close
description: "End-of-session hand-off for this repo. Use when finishing work; updates koder/STATE.md under 100 lines, runs relevant checks, and commits the semantic state transition with a grepable state: close subject."
---

# Close Session

Use this skill at the end of a work session in this repository.

## Steps

1. Inspect current state, including staged work:
   ```bash
   git status --short
   git diff --stat
   git diff --cached --name-only
   ```
   If this is not a git repository, initialize it with `git init` before the state commit.
2. Refresh `koder/STATE.md` frontmatter timestamp:
   - Ensure the file starts with YAML frontmatter containing `updated_at`.
   - Set `updated_at` to current India time in this exact format: `DD Mon YYYY | HH:MM AM IST`.
   - Use:
     ```bash
     TZ='Asia/Kolkata' date '+%d %b %Y | %I:%M %p IST'
     ```
3. Update `koder/STATE.md` so it remains under 100 lines and accurately captures:
   - Past: durable completed work from this session.
   - Present: current repo structure/state and any important caveats.
   - Future: concise next steps for the next session.
4. Verify line count:
   ```bash
   wc -l koder/STATE.md
   ```
   If it is 100 lines or more, compress it before continuing.
5. Run relevant checks/tests if the repo defines any. If none exist, note that no test suite is present.
6. Review final changes:
   ```bash
   git status --short
   git diff --stat
   git diff --cached --name-only
   ```
7. Commit intentional safe work with a `state: close` subject:
   - Use `state: close - <semantic session result>`.
   - Stage only intentional safe paths; avoid blind `git add -A` when unrelated dirty work exists.
   - If committing only handoff state, use a path-scoped commit for `koder/STATE.md` and relevant `koder/` artifacts.
   - If committing broader session work, ensure secrets/caches/generated outputs/unrelated paths are excluded.
   - Include this body shape:
     ```text
     State event: close
     State file: koder/STATE.md
     Session result: <one line>

     Delta:
     - <semantic movement completed this session>
     - <operator-facing next state>

     Validation:
     - <commands/checks/manual validation>
     ```
8. Confirm final repository state:
   ```bash
   git status --short
   git log --grep='^state:' --oneline -5
   ```
   If intentional work remains uncommitted, explain exactly why and list the paths.

## Rules

- Every intentional `koder/` state transition gets a `state:` commit unless the user explicitly says not to commit.
- Do not commit secrets, credentials, caches, build outputs, or unrelated generated files.
- Do not sweep unrelated dirty/staged work into a state commit.
- Keep `koder/STATE.md` concise; it is a session handoff, not the `state:` commit ledger or a changelog.
- Always update `updated_at` in `koder/STATE.md` frontmatter using India time format: `DD Mon YYYY | HH:MM AM IST`.
