---
name: update-branch
description: "Update the current feature branch with its base branch — the same as GitHub's Update branch button. Merges the base (the branch the feature was created from, usually main) into the feature branch and resolves conflicts. Use when: user says 'update branch', 'sync my branch', or the PR shows 'This branch is out-of-date with the base branch'."
---

# Update Branch from Base

Bring the current feature branch up to date with its **base branch** — the exact operation GitHub's **Update branch** button performs. It merges the base branch (the branch this feature was created from — usually `main`) **into** the current branch with a merge commit, then resolves any conflicts.

## Repository Scope

Operates on **this repository** (the workspace root).

## Key Rules

- **REBASE IS FORBIDDEN.** Never use `git rebase`. Always merge the base branch into the feature branch — rebase rewrites history and is dangerous on a branch that already has an open PR.
- This skill is for **feature branches**, not `main`. To update `main` itself, use `/latest`.
- This skill does **not** create a PR — it merges, resolves conflicts, commits, and pushes the updated branch. The existing PR updates automatically.

## User Input (optional)

An explicit base branch, when the feature was not branched from `main` (e.g. "update branch from `release/v5`"). When omitted, the base is resolved automatically.

## 1. Verify the Branch

```
git status
git branch --show-current
```

- **If on `main`**: stop. This skill updates a feature branch. Use `/latest` to update `main` instead.
- **If there are uncommitted changes**: **stop**. Commit them first (e.g. via `/ship`) — never merge on top of a dirty working tree, and never `git stash` to clear it.
- **If the working tree is clean and on a feature branch**: continue.

## 2. Resolve the Base Branch

Determine which branch this feature should be updated from, in priority order:

1. **Explicit base** the user supplied in the request.
2. **The open PR's base** — read `baseRefName` from the PR for the current branch:

   ```
   gh pr view --json baseRefName --jq .baseRefName 2>&1
   ```

3. **Fallback to `main`** when there is no open PR and the user gave no base.

Use the resolved name as `<base>` for the remaining steps.

## 3. Fetch and Merge the Base

```
git fetch origin <base>
git merge origin/<base> --no-edit
```

Branch on the result:

- **"Already up to date."** — nothing to merge. Report to the user and stop.
- **Clean merge** — the merge commit was created with no conflicts. Skip to **step 5**.
- **Conflicts** — git lists conflicted paths. Proceed to **step 4**.

## 4. Resolve Conflicts

```
git diff --name-only --diff-filter=U
```

Resolve each conflicted file by understanding **what** each side changed and **why** — preserve the feature branch's intent while integrating updates from the base. Never blindly accept one side.

Follow the repository conventions when resolving:
- **Markdown / docs** — keep both additions when changes are purely additive (e.g. two new rows in a README table). Preserve YAML front matter, CRLF line endings, UTF-8 without BOM, and emojis exactly.
- **Mermaid diagrams** — keep both nodes/edges when additive; reconcile counts and labels if the same diagram changed on both sides.
- **Definition links** — never collapse a linked metadata value back to plain text.

After resolving, confirm no conflict markers remain:

```
git diff --check
git diff --name-only --diff-filter=U
```

If unresolved conflicts remain, **stop** and report — never commit a partial resolution. Otherwise stage and commit the merge:

```
git add -A
git commit --no-edit
```

## 5. Validate

Run the repository validation scripts from the workspace root to confirm the merge did not break the build (the same checks the `/validate` prompt runs):

```
python .github/scripts/check-github-pages.py .
python .github/scripts/check-github-structure.py .
python .github/scripts/check-markdown-links.py .
python .github/scripts/check-markdown-tables.py .
python .github/scripts/check-mermaid-diagrams.py .
```

If any script exits non-zero, fix the issue, commit the fix, and re-run. If it still fails after a reasonable attempt, report to the user and stop.

## 6. Push

```
git push
```

This updates the existing PR. **Never** use `--force`, and never push to `main`.

## 7. Report

Tell the user:
- The feature branch name and the base branch it was merged with
- Merge result (clean / conflicts resolved / already up to date)
- For conflicts: which files and how each was resolved
- Validation status
- That the existing PR was updated (no new PR created)

## Safety Rules

See the `github` skill §8 (Git Safety Rules). Key points:
- **Never** `git rebase` — always merge
- **Never** `git stash`, `git reset --hard`, `git clean`, or discard uncommitted work
- **Never** `--force` push
- **Never** push to `main` directly
