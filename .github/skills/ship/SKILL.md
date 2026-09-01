---
name: ship
description: "Ship changes via pull request. Use when: user says 'ship', wants to commit, push, or submit changes for review."
---

# Ship — Submit Changes via Pull Request

**NEVER commit or push directly to `main`.** All changes go through a pull request.

This flow is **script-driven**: a preflight script decides the single correct path,
and three follow-up scripts perform the mechanical git/gh steps deterministically.
Do **not** improvise git or gh command sequences — call the scripts below and read
their `KEY=value` output. The only judgment you supply is the **branch name**, the
**commit message**, and the **PR title/body** (content, not procedure).

> Submodule pointer bumps are never part of a normal ship PR. If the working tree
> has submodule **gitlink** drift (a clone under `sources/` sitting at a different
> commit than the base branch records), `commit-and-push.ps1` deliberately excludes
> it from the commit and reports what it dropped.

## Destructive Git Operations — NEVER Without Permission

See the `github` skill §8 (Git Safety Rules) for the full list. Forbidden commands
include `git stash`, `git clean`, `git checkout -- .`, `git restore .`,
`git reset --hard`, and switching to an existing branch with a dirty working tree.
The scripts below never run these; do not run them yourself to "help" a script.

**Key principle:** When in doubt, **commit and push what you have** to the current
branch. A messy commit on a feature branch is infinitely better than lost work.

## 1. Preflight — Detect the Situation

Run the preflight. It is read-only (no commits, branch changes, or pushes):

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/ship-preflight.ps1"
```

Read the `KEY=value` output. The `ACTION` value selects exactly one path in step 2.
If `RESULT` is `stopped-not-a-git-repo` or `stopped-detached-head`, report
`STOP_REASON` to the user and stop.

If `SUBMODULE_CHANGES` is non-empty, mention the excluded paths to the user so the
drop is not a surprise.

> Ships into a branch other than `main`? Every script below takes `-Base <branch>`.

## 2. Act on the `ACTION`

Pick the **one** row matching the preflight `ACTION` and follow only that row.

| `ACTION` | What it means | Do this |
|---|---|---|
| `stop-no-changes` | Working tree clean | Inform the user there is nothing to ship and stop. |
| `commit-push` | On a feature branch with an **open** PR | **Step 3** (commit + push). Do **not** create a PR. |
| `commit-push-pr` | Feature branch, PR closed or none | **Step 3** (commit + push), then **step 5** (create PR). |
| `branch-commit-push-pr` | On `main` with changes | **Step 3** with `-NewBranch`, then **step 5** (create PR). |
| `squash-recovery` | Feature branch whose PR is already **merged** | **Step 4** (rebase onto fresh `main`), then **step 5** (create PR). |

## 3. Commit and Push

Run the commit/push script. Supply a commit message (use the user's if given,
otherwise generate one from the diff). For the `branch-commit-push-pr` action,
also pass `-NewBranch ai/<short-description>` (lowercase kebab-case, max 5 words)
so the work moves off `main` onto a fresh branch before committing:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/commit-and-push.ps1" `
  -CommitMessage "<descriptive commit message>"
```

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/commit-and-push.ps1" `
  -NewBranch "ai/<short-description>" -CommitMessage "<descriptive commit message>"
```

Read the output:

- `RESULT=pushed` — committed (if needed) and pushed. Note `BRANCH`. Continue to
  step 5 only if your `ACTION` row says to create a PR; otherwise go to step 6.
  If `SKIPPED_SUBMODULES` is non-empty, the listed submodule gitlink changes were
  intentionally left out of the commit — report them to the user.
- Any `RESULT=stopped-*` — the script made no commit/push; read `STOP_REASON`
  (e.g. `on-base-without-newbranch`, `missing-commit-message`, `branch-exists`)
  and fix the precondition before re-running.

## 4. Squash-Merge Recovery (rebase onto fresh `main`)

Reach this step only when `ACTION=squash-recovery` — the current branch's PR is
already **merged**, so it is stale and must not be reused. Squash-merged PRs put a
single commit on `main`, so the branch's own commits are not in that history and
committing on top of it would make every merged-PR file reappear in the next PR.

Run the deterministic recovery script — it captures the work, fetches `main`,
creates the fresh branch, cherry-picks, and verifies in one non-destructive pass:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/rebase-onto-base.ps1" `
  -NewBranch "ai/<short-description>" -CommitMessage "<descriptive commit message>"
```

- **Dirty working tree (common case):** the script commits the changes as a single
  squash-immune commit and cherry-picks it onto a fresh branch from `origin/main`.
  Pass `-CommitMessage`.
- **Work already committed on the stale branch (clean tree):** name the commit
  hash(es) to move with `-CherryPick <hash> [<hash> ...]` (squash hides the link,
  so they cannot be auto-detected).

Read the output:

- `RESULT=rebased` — success; you are on `NEW_BRANCH`. Confirm `DIFF_FILE_COUNT`
  matches the number of files you intended to change. Push it, then create the PR:

  ```powershell
  powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/commit-and-push.ps1"
  ```

  (No `-CommitMessage` needed — the work is already committed, so this only pushes.)
  Then continue to step 5.
- `RESULT=conflicts` — a cherry-pick conflict (the one non-deterministic part). The
  cherry-pick is left **in progress** so nothing is lost. Resolve the files in
  `CONFLICT_FILES`, run `git cherry-pick --continue` until `CHERRY_REMAINING` is
  empty, then push with the same `commit-and-push.ps1` call above.
- Any `RESULT=stopped-*` — no changes made; read `STOP_REASON` and fix the
  precondition before re-running.

## 5. Create the Pull Request

Only when your `ACTION` row directs you here. First **author the PR body with your
file-creation tool** — write the markdown (a bullet list of what changed and why)
to a UTF-8 file under the temp directory (e.g. `$env:TEMP\pr-body.md`). Do **not**
round-trip the body through a shell variable. Then run:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/create-pr.ps1" `
  -Title "<concise summary>" -BodyFile "$env:TEMP\pr-body.md"
```

The script is idempotent: if an open PR already exists it returns that one
(`RESULT=already-exists`) instead of opening a duplicate. Read `PR_URL` from the
output. Any `RESULT=stopped-*` — read `STOP_REASON` (e.g. `body-file-missing`,
`on-base`) and fix it before re-running.

## 6. Report

Tell the user:

- The PR link (`PR_URL` — newly created or already existing)
- They should review it in the GitHub UI
- CI checks will run automatically
- Merge when checks pass and review is complete

## IMPORTANT

See the `github` skill §8 for the full safety rules. Key points:

- NEVER push to `main` directly — always create a PR
- NEVER commit submodule pointer bumps in a normal ship PR.
  `commit-and-push.ps1` drops staged submodule gitlink changes from the commit.
- NEVER use `--force` push
- NEVER stash, clean, or discard changes — commit them instead
- NEVER switch branches with uncommitted work — let the scripts create a new branch at HEAD instead
- NEVER create a new branch when there's already an active feature branch with an **open** PR — the preflight routes this to `commit-push`
- NEVER push more commits to, or branch off, a branch whose PR is already **merged** — the preflight routes this to `squash-recovery` (step 4)
