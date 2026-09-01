---
name: ship
description: "Ship changes via pull request. Use when: user says 'ship', wants to commit, push, or submit changes for review."
---

# Ship — Submit Changes via Pull Request

**NEVER commit or push directly to `main`.** All changes go through a pull request.

Run all git and gh commands in the terminal. Follow these steps exactly:

## Destructive Git Operations — NEVER Without Permission

See the `github` skill §8 (Git Safety Rules) for the full list. The forbidden commands include: `git stash`, `git clean`, `git checkout -- .`, `git restore .`, `git reset --hard`, and switching branches with dirty working tree.

**Key principle:** When in doubt, **commit and push what you have** to the current branch. A messy commit on a feature branch is infinitely better than lost work.

## 1. Check Status

```
git status
```

- If there are no changes (staged or unstaged), inform the user and stop.
- Note which branch you are on — this determines the flow below.

## 2. Determine Flow

**If on a feature branch with an open PR**: this is the most common case. Push directly to it — go to step 4. Do NOT create a new branch. Do NOT switch branches. Do NOT stash.

```
gh pr view --json state,number,url 2>&1
```

- **Open PR exists** (`"state":"OPEN"`): skip step 3, go directly to step 4.

**If on a feature branch whose PR is already `MERGED`**: the branch is stale and **must not** be reused. Most PRs here are **squash-merged**, so the branch's individual commits are *not* in `main`'s history — `main` has a single squashed commit instead. If you commit on top of this branch or branch off it, every file from the merged PR reappears as "new" and pollutes the next PR. Instead, move only your new work onto a fresh branch cut from the latest `main` — go to **step 2a**.

**If on a feature branch with a `CLOSED` (not merged) PR, or no PR at all**: the branch is not in `main`. You may continue on it — commit current changes (step 4), then create a new PR if none exists (step 6).

**If on `main`**: proceed to step 3 to create a new feature branch.

**NEVER switch away from a branch that has uncommitted changes.** If you need to be on a different branch, **commit first** (so the work is captured as a recoverable commit), then switch.

## 2a. Re-base Work Off a Merged Branch (squash-merge recovery)

Reach this step only when the current branch's PR is already `MERGED` and you have new uncommitted (or unpushed) work to ship.

1. **Capture the work as a commit** on the current stale branch so it is safe and has a hash:

   ```
   git add -A
   git commit -m "<descriptive commit message>"
   ```

   Record the resulting hash (`git rev-parse HEAD`).

2. **Update `main`:**

   ```
   git checkout main
   git pull origin main
   ```

3. **Create a fresh branch from the updated `main`:**

   ```
   git checkout -b ai/<short-description>
   ```

4. **Cherry-pick your commit(s)** onto the clean branch (use the hash(es) from step 1):

   ```
   git cherry-pick <hash>
   ```

5. **Verify only your intended files differ** from `main` — there must be **no** files from the already-merged PR:

   ```
   git diff --name-only origin/main...HEAD
   ```

   If unexpected files appear, stop and investigate before pushing.

6. Push the clean branch (step 5) and create a new PR (step 6).

> The original stale branch is left untouched. Do not delete it unless the user asks — its commit history is harmless once your work lives on the new branch.

## 3. Create a Feature Branch (only from clean `main`)

Only reach this step from `main` with no uncommitted changes.

```
git pull
git checkout -b ai/<short-description>
```

Generate a branch name using `ai/<short-description>` (lowercase, kebab-case, max 5 words).

## 4. Stage and Commit

```
git add -A
git commit -m "<descriptive commit message>"
```

If the user provides a commit message, use it; otherwise generate one from the diff.

## 5. Push

```
git push -u origin <current-branch>
```

## 6. Create Pull Request (only if one doesn't exist yet)

Check if a PR already exists for the current branch:

```
gh pr view --json number,url 2>&1
```

- **If a PR already exists**: skip PR creation — just report the existing PR link.
- **If no PR exists**: create one. Author the body in a **single-quoted** here-string (`@'...'@`) written to a UTF-8 (no BOM) file and post with `--body-file` — never an inline `--body "..."` or a double-quoted here-string (`@"..."@`), which corrupts backticks/markdown. See `github` skill §3 (Posting body text safely):

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$body = @'
<bullet-point list of what changed and why>
'@
[System.IO.File]::WriteAllText("$env:TEMP\pr-body.md", $body, $utf8NoBom)
gh pr create --base main --head <current-branch> --title "<title>" --body-file "$env:TEMP\pr-body.md"
```

- **Title:** concise summary of the changes
- **Body:** bullet-point list of what changed and why.

## 7. Report

Tell the user:
- The PR was created (or already existed) with the link
- They should review it in the GitHub UI
- CI checks will run automatically
- Merge when checks pass and review is complete

## IMPORTANT

See the `github` skill §8 for the full safety rules. Key points:
- NEVER push to `main` directly — always create a PR
- NEVER use `--force` push
- NEVER stash, clean, or discard changes — commit them instead
- NEVER switch branches with uncommitted work — commit first, then switch
- NEVER create a new branch when there's already an active feature branch with an **open** PR — push to the existing one
- NEVER push more commits to, or branch off, a branch whose PR is already **merged** — squash-merge means its files would re-enter the next PR. Re-base your work onto a fresh branch cut from latest `main` (step 2a) and verify with `git diff --name-only origin/main...HEAD` that only your intended files appear.
