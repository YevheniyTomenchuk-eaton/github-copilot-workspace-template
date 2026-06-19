---
description: "Switch to the main branch and pull the latest commits. Use when: user says 'latest', 'pull main', 'update main', 'checkout main and pull', or wants their local main up to date."
agent: "agent"
---

# Latest — Update Local `main`

Bring the local `main` branch up to date with `origin/main`. This is a read-only-ish, safe operation — it never commits, pushes, or discards work.

## Repository Scope

Operates on **this repository** (the workspace root).

## 1. Check the Current Branch and Working Tree

```
git status
git branch --show-current
```

- **If the working tree is dirty** (staged or unstaged changes — on `main` or any other branch): **stop** unconditionally. Do **not** switch branches *or* pull — both risk losing or entangling uncommitted work. Tell the user to commit first (e.g. via `/ship`), then re-run. There is **no** "confirm to proceed" path — this prompt always refuses to act on a dirty working tree.
- **If already on `main`** with a clean working tree: no branch switch is needed — skip to **step 2b** and just pull.
- **If on another branch with a clean working tree**: continue to **step 2a**.

## 2a. Switch to `main`

```
git checkout main
```

## 2b. Pull the Latest Commits

```
git pull --ff-only
```

## 3. Report

Tell the user:
- The branch is now `main`
- Whether new commits were pulled (and a one-line summary of what arrived), or that it was already up to date

## Safety Rules

See the `github` skill §8 (Git Safety Rules). Key points:
- **Never** switch branches with uncommitted changes — stop and let the user commit first
- **Never** `git stash`, `git reset --hard`, `git clean`, or `git checkout -- .` to "make room" for the checkout
- This prompt does not create branches, commit, or push — use `/ship` for that
