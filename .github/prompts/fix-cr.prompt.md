---
description: "Review and resolve open review comments from ALL reviewers (human and Copilot) and failing CI checks on the current CR. Use when: user wants to check CR feedback, fix issues, resolve threads, and fix CI failures."
agent: "agent"
---

# Fix CR — Resolve Review Comments and CI Failures

Fetch open review threads and check CI status on the current CR. Validate each issue, fix what's valid, reply, and resolve.

**Address every reviewer's comments — not only Copilot's.** Human reviewers and Copilot both open review threads; treat them identically and select threads by `isResolved` alone, never by author. Requesting a fresh Copilot review at the end is only a convenience for the next automated pass — it never narrows which comments get addressed in this one.

**Address global comments, not only inline threads.** Inline review threads are only one of three feedback surfaces. Reviewers also leave **PR-level** feedback that has **no resolve affordance**: **issue comments** (the PR Conversation timeline) and **review summary bodies** (the prose typed when submitting a review). A reviewer's most important note is often a single global comment with **no inline thread** — fetch and address those too (step 2).

**This is a single non-blocking pass.** Scan what is available **right now** — currently-open review threads and checks that have **already failed** — fix them, reply, resolve, request a fresh Copilot review, and exit. **Never wait or poll** for in-progress CI or for Copilot to come back.

## 1. Identify the CR

```
gh pr view --json number,url,state
```

If no open CR exists, inform the user and stop.

## 2. Fetch Open Review Threads

Use the `github` skill §2 (Repository Identification) to get `<OWNER>` and `<REPO>`, then §4 (Fetch all review threads) — **the paginated version**. A single `first: 100` call is forbidden: PRs with more than 100 threads silently drop the rest and unresolved comments will be missed.

After fetching, assert `$allThreads.Count -eq $totalCount` before filtering. If the assertion fails, stop and report — never proceed on a partial list.

Filter for `isResolved: false` — **across all authors** (human reviewers and Copilot alike). Never filter by author. If every thread is resolved, inform the user and proceed to step 6.

Then fetch **PR-level (global) comments** with the `github` skill §4 (Fetch PR-level global comments):

```powershell
powershell.exe -ExecutionPolicy Bypass -File ".github/scripts/github/fetch-pr-comments.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER>
```

Read the `OUT_FILE` JSON (`issueComments[]`, `reviewSummaries[]`). Ignore pure-noise summaries (Copilot's "## Pull request overview … generated N comments" boilerplate, a bare "need fixes" with no specifics). For every global comment with a concrete request, make the change in steps 3–4. You do **not** post a separate reply per global comment: a **human** global comment is acknowledged in the **single global summary comment** (step 9) by @-tagging the author and noting what changed; a **Copilot** global comment (`*copilot*` author) is acted on but **never acknowledged** — its summary is convergence boilerplate it never reads. Global comments cannot be resolved — never fabricate a thread to resolve.

## 3. Validate Each Open Comment

For each unresolved thread:

1. **Read the file** at the path and line mentioned in the comment
2. **Understand the suggestion** — what is the reviewer asking for?
3. **Check against the source of truth** — read related files to determine if the comment is valid
4. **Classify** as: valid, invalid, or partially valid

## 4. Act on Each Comment

- **Valid**: Fix the issue in the file, then reply explaining what was fixed
- **Invalid**: Reply explaining why the suggestion doesn't apply (citing the source of truth or convention)
- **Partially valid**: Fix what applies, reply explaining what was fixed and what was skipped and why

## 5. Reply and Resolve Threads

For each thread, **always reply before resolving** — never resolve a thread silently.

**IMPORTANT:** Run the reply and resolve as **separate terminal commands** (see `github` skill §4). Author every reply body via a single-quoted here-string written to a file and pass it with `--input` / `--body-file` (`github` skill §3) — never an inline `-f body="..."` with backticks or em-dashes, which corrupts the text. If the reply command output is truncated or unclear, **read** the thread before retrying — never re-run a mutation, it posts a duplicate comment.

Reply to the thread, then resolve it using the GraphQL mutations from the `github` skill §4 (Reply to a thread, Resolve a thread).

**Reply content by classification:**
- **Valid**: "Fixed — [describe what was changed]."
- **Invalid**: "Not applicable — [explain why, citing source of truth]."
- **Partially valid**: "Partially fixed — [what was changed]. Skipped [what was not changed] because [reason]."

## 6. Check CI Status

Take a **single snapshot** of CI status using the `github` skill §7 — run the check command **once**. **Do not wait or poll** for `PENDING` / `QUEUED` checks to finish (no `--watch`, no `Start-Sleep` loop). Act only on checks that are **already** in `FAILURE`. If every completed check passed, skip to step 8. If any have already failed, proceed to step 7. Note any still-running checks in the final report and move on.

## 7. Fix Failing Checks

For each failing check:

1. **Read the failure details** — use the `github` skill §7 to get failed run logs

2. **Diagnose the failure** — read the relevant file(s) and understand what the CI check is validating
3. **Classify** the failure:
   - **Valid failure** (real issue in the CR): fix the file(s)
   - **Flaky / infrastructure issue** (network timeout, runner problem): inform the user, suggest re-running
   - **Pre-existing failure** (was already failing before this CR): inform the user, skip
4. **Fix valid failures** — edit the file(s) to resolve the issue

## 8. Commit and Push

If any files were modified:

```
git add -A
git commit -m "fix: resolve CR review comments"
git push
```

## 9. Post Global Summary Comment

After pushing, add a single CR-level comment summarizing all changes made in this pass. **Author the body via a single-quoted here-string written to a UTF-8 (no BOM) file and post with `--body-file`** — never an inline `--body "..."` and never a double-quoted here-string (`@"..."@`), which corrupts backticks/markdown and can post phantom duplicates. See `github` skill §3 (Posting body text safely).

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$summary = @'
<SUMMARY>
'@
[System.IO.File]::WriteAllText("$env:TEMP\cr-summary.md", $summary, $utf8NoBom)
gh pr comment <NUMBER> --body-file "$env:TEMP\cr-summary.md"
```

Post **exactly once**. If the command output is unclear, re-read the PR comments to confirm — do **not** re-run the post (it creates a duplicate).

The summary should list:
- Each review thread addressed (file + what was fixed or why it was skipped)
- Each **human global comment** addressed — **@-tag the author** and note what was fixed (this is the acknowledgement; do not post a separate reply). Never mention Copilot's summary bodies here.
- Each CI failure addressed (check name + what was fixed)
- Any remaining issues that could not be resolved automatically

## 10. Verify All Threads Resolved

Re-fetch review threads using the **paginated** query from step 2 (`github` skill §4). Assert `$allThreads.Count -eq $totalCount` — a partial fetch hides unresolved threads.

Then count `$unresolved = @($allThreads | Where-Object { -not $_.isResolved })`. If `$unresolved.Count -gt 0`, **do not proceed to step 11** — print the list of unresolved thread IDs and the first 200 characters of each latest comment, then go back to step 3 for those threads.

Only continue to step 11 when `$unresolved.Count -eq 0` AND `$allThreads.Count -eq $totalCount`.

## 11. Request Copilot Code Review

After all threads are resolved and changes are pushed, request a fresh Copilot code review using the `github` skill §6 (Request Copilot re-review), then **exit**. This is **fire-and-forget** — do **not** poll or wait for the review to come back. Verify only that the request itself succeeded (the response contains reviewer data, not an error).

## 12. Report

Summarize for the user:
- How many review threads were open and how many were valid / invalid / partial
- How many **global comments** (issue comments + review summaries) were addressed, by author
- How many CI checks had already failed and how many were fixed / flaky / pre-existing
- Any checks still running that were **not** waited on
- What was fixed
- Current status: all threads resolved, already-failed checks addressed (or what remains)
- That a fresh Copilot review was requested (fire-and-forget — not waited on)
