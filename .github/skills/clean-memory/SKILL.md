---
name: clean-memory
description: "Delete all AI memory files — user preferences, repo memory, and session notes. Enforces the project policy that all persistent knowledge belongs in .github/instructions/ files."
---

# Clean AI Memory

Delete all AI memory files associated with this workspace. This project stores all persistent knowledge in `.github/instructions/` files — hidden memory files must not exist.

## Steps

1. List all files under `/memories/` (user memory, session memory, repo memory)
2. Delete every file and directory found:
   - `/memories/*.md` — user preferences
   - `/memories/repo/*.md` — repo-scoped memory
   - `/memories/session/*.md` — session scratch notes
3. Verify `/memories/` is empty after cleanup
4. Report what was deleted

## Rules

- Delete everything — no exceptions
- Do not move content to `.github/instructions/` automatically. If a memory file contains useful content, report it to the user before deleting so they can decide whether to preserve it in an instruction file
- Do not create new memory files after cleanup
