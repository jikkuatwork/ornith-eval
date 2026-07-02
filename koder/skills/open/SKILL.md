---
name: open
description: Start-of-session hand-off for this repo. Use when beginning work in this project; reads koder/STATE.md, inspects repository status, and summarizes past/present/future context before changes.
---

# Open Session

Use this skill at the beginning of a work session in this repository.

## Steps

1. Locate the repository/project root from the current working directory.
2. Read `koder/STATE.md` completely before making changes.
3. Check repository state:
   ```bash
   git status --short
   git branch --show-current
   git log --oneline -5
   ```
   If this is not a git repository, say so clearly and continue with the file-based hand-off.
4. Summarize:
   - Past: what was previously done.
   - Present: current repo state and any dirty/uncommitted work.
   - Future: next likely tasks or risks.
5. Ask what the user wants to do next unless they already gave a concrete task.

## Rules

- Do not modify files as part of opening unless the user explicitly asks.
- Treat `koder/STATE.md` as the source of truth for cross-session context.
- If `koder/STATE.md` is missing, tell the user and offer to create it.
