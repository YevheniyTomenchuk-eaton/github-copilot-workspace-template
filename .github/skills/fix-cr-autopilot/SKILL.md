---
name: fix-cr-autopilot
description: "Autopilot loop: resolve ALL reviewers' review comments (human and Copilot), request re-review, wait for completion, repeat until no new comments remain. Use when: user wants fully automated CR cleanup."
---

# Fix CR Autopilot — Loop Until the CR Is Clean

Automated loop: fix review threads → push → request Copilot re-review → wait for completion → check for new threads → repeat until the CR has zero unresolved threads and Copilot returns no new comments.

**Address every reviewer's comments — not only Copilot's.** Human reviewers and Copilot both open review threads. The loop fixes, replies to, and resolves *all* unresolved threads regardless of author. Copilot re-review is used only as the automated convergence signal (a human cannot be asked to re-review on demand); it never narrows *which* comments get addressed.

**Address global comments, not only inline threads.** Review threads (inline file comments) are only one of three feedback surfaces. The other two are **PR-level** and have **no resolve affordance**: **issue comments** (the PR Conversation timeline) and **review summary bodies** (the prose typed when submitting a review). Reviewers — humans especially — frequently leave their most important guidance as a single global comment with **no inline thread at all** ("need fixes", "follow the convention here", a paragraph of direction). A thread-only loop would declare the CR clean while that instruction sits unread. Every cycle must fetch and address global comments too (see Step A).

## 1. Identify the CR

```
gh pr view --json number,url,state
```

If no open CR exists, inform the user and stop.

Get `<OWNER>` and `<REPO>` using the `github` skill §2 (Repository Identification).

Record a **baseline timestamp** now — the current UTC time, formatted ISO8601 (e.g. `2026-06-12T04:00:00Z`). Each cycle fetches global comments created **after** the previous cycle's timestamp, so the same global note is never re-addressed (global comments have no resolved flag to track state). Initialize `$sinceGlobal` to this baseline.

## 2. Start the Loop

Initialize a cycle counter at 1. Each cycle consists of: fetch → fix → push → request review → wait → check.

---

### Cycle Step A: Fetch Unresolved Threads

Fetch all review threads using the `github` skill §4 (Fetch all review threads) — **the paginated version**. After fetching, assert `$allThreads.Count -eq $totalCount`. A single `first: 100` call is forbidden: PRs with more than 100 threads silently drop the rest, which causes the loop to declare convergence prematurely.

Filter unresolved threads from `$allThreads` only after the count matches `totalCount`.

**Filter rule:** A thread is unresolved when `isResolved -eq $false`, **regardless of who authored it** — human reviewers and Copilot are treated identically. **Never** narrow the filter to a single author (e.g. `author.login -like "*copilot*"`); doing so silently skips every human reviewer's thread. **Do NOT filter out `isOutdated` threads** either — `isOutdated` only means the surrounding code changed since the comment was posted; the underlying issue may still be valid. The correct filter is:

```powershell
$unresolved = @($allThreads | Where-Object { -not $_.isResolved })
```

For each `isOutdated` unresolved thread, re-read the file at the comment's path to determine whether the issue still applies. If the code has already been fixed elsewhere, reply "Already addressed — [reference]" and resolve. If the issue persists, fix it normally.

**Also fetch PR-level (global) comments.** Run the `github` skill §4 (Fetch PR-level global comments) with `-Since $sinceGlobal` so only comments newer than the previous cycle are returned:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/fetch-pr-comments.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER> -Since "$sinceGlobal"
```

Read the `OUT_FILE` JSON: `issueComments[]` and `reviewSummaries[]`. For each global comment, **ignore pure-noise summaries** (Copilot's "## Pull request overview … generated N comments" boilerplate carries no actionable ask beyond the inline threads it already filed; a human "need fixes" with no specifics is also non-actionable on its own). For every global comment that **does** contain a concrete request, make the change. You do **not** post a separate reply per global comment — the acknowledgement is handled **by author**:

- **Human global comment** → record the author and what you changed; fold it into the **single consolidated summary comment** posted in Step E, **@-tagging the author** there (not a reply per comment).
- **Copilot global comment** (`*copilot*` author) → act on anything concrete but **never acknowledge it** — its summary is convergence boilerplate Copilot never reads; its real asks are the inline threads you already handle.

Global comments cannot be resolved — never fabricate a thread to resolve. After processing, advance `$sinceGlobal` to the newest `submittedAt`/`createdAt` you handled (or the current UTC time) so the next cycle starts fresh.

**Convergence now depends on BOTH surfaces.** The loop is complete only when there are zero unresolved threads **and** no unaddressed actionable global comments. If unresolved threads are zero but a new actionable global comment exists, the cycle is **not** done — address it before checking CI.

If zero unresolved threads exist and this is cycle 1, proceed to **Step D** (check CI) and then to **Step F** (request review to generate initial feedback). Fix any CI failures before requesting the review.

If zero unresolved threads exist **and** no actionable global comments remain and this is cycle 2+, the loop is complete — go to **Step H** (report).

### Cycle Step B: Validate Each Comment

For each unresolved thread:

1. **Read the file** at the path and line mentioned in the comment
2. **Understand the suggestion** — what is the reviewer asking for?
3. **Check against the source of truth** — read related files to determine if the comment is valid
4. **Classify** as: valid, invalid, or partially valid

**Critically evaluate each comment — but evaluate by content, not by author.** Some AI review comments are noise: redundant suggestions, overengineering proposals, or complaints about things already handled elsewhere in the code. Human comments are usually substantive and may require real design changes. Judge every thread on its merits and classify it; do not blindly fix everything, and do not skip a thread just because of who wrote it.

### Cycle Step C: Fix and Reply

- **Valid**: Fix the issue in the file
- **Invalid**: Skip the fix
- **Partially valid**: Fix only what applies

**Reply to every thread before resolving.** Run reply and resolve as **separate terminal commands** (see `github` skill §4).

Reply and resolve each thread using the GraphQL mutations from the `github` skill §4 (Reply to a thread, Resolve a thread).

**Reply content:**
- **Valid**: "Fixed — [what was changed]."
- **Invalid**: "Not applicable — [why, citing source of truth]."
- **Partially valid**: "Partially fixed — [what changed]. Skipped [what didn't] because [reason]."

### Cycle Step D: Check CI

Check CI using the `github` skill §7. If any checks have `state: FAILURE`:

1. Get logs using the skill §7 (Get failed run logs)
2. Fix valid failures, inform user about flaky/pre-existing ones

### Cycle Step E: Commit and Push

If any files were modified:

```
git add -A
git commit -m "fix: resolve CR review comments (cycle <N>)"
git push
```

**If no files were modified** (all threads were invalid), skip the commit/push but **still proceed to Step F.** Never declare convergence here — convergence is only checked at Step A of the next cycle, after a fresh Copilot review.

**If this cycle addressed any human global comments** (Step A), post **one consolidated PR-level summary comment** after pushing — author the body per the `github` skill §3 (single-quoted here-string → UTF-8 no-BOM file → `gh pr comment <NUMBER> --body-file ...`), **@-tag each human author** whose global comment you addressed, and list what changed for each. This is a **single** summary, never a reply per comment, and never mentions Copilot's summaries. Post exactly once; if the output is unclear, re-read the PR comments rather than re-running (a re-run posts a duplicate).

### Cycle Step F: Request Copilot Re-Review

First, record the current review count using the `github` skill §5 (List all reviews with pagination):

```powershell
$reviews = gh api repos/<OWNER>/<REPO>/pulls/<NUMBER>/reviews --paginate | ConvertFrom-Json
$copilotReviews = @($reviews | Where-Object { $_.user.login -like "*copilot*" })
$reviewCountBefore = $copilotReviews.Count
"Copilot reviews before request: $reviewCountBefore"
```

Then request the review using the `github` skill §6 (Request Copilot re-review). See the skill for the critical Copilot identifier table — using the wrong name silently fails.

### Cycle Step G: Wait for Copilot Review Completion

Use the polling script from the `github` skill §6 (Poll for Copilot review completion). **Run it in sync mode with a generous timeout (e.g. 1400000 ms / ~23 min)** so the loop blocks your turn until one of the sentinel strings is emitted. Replace `<REVIEW_COUNT_BEFORE>` with the value recorded in Step F.

**Do NOT use async mode here.** Async mode caused historical autopilot stalls: the agent would launch the poll, see `WAITING:` lines, and incorrectly treat the turn as finished — leaving the loop dangling. Sync mode keeps the agent in the same turn until the poll terminates.

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/poll-copilot-review.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER> -ReviewCountBefore <REVIEW_COUNT_BEFORE> -Quiet
```

The sync call blocks until the loop emits one of the sentinel strings — no `get_terminal_output` polling needed. When it returns `COPILOT_DONE`, `COPILOT_SILENT`, or `COPILOT_TIMEOUT`, proceed:

- **`COPILOT_DONE`**: New review submitted. Increment cycle counter, go back to **Step A**.
- **`COPILOT_SILENT`**: Copilot left the pending list without a new review. This means it found nothing new to comment on. Go to **Step H** (report success).
- **`COPILOT_TIMEOUT`**: Copilot is stuck. Report the timeout to the user and stop.

**Important:** `Start-Sleep` is allowed inside this polling script even under sync mode — the agent-level prohibition on `Start-Sleep` applies only to standalone wait commands, not to the body of a long-running poll. The internal 10-minute cap inside the script guarantees the sync call will return before the 11.5-minute tool timeout fires.

**Autopilot continuation rule:** After the sync call returns with `COPILOT_DONE`, immediately continue the loop in the SAME turn — fetch unresolved threads (Step A) and proceed. Never end the turn between cycles. The loop runs unattended until one of these terminal conditions: `COPILOT_SILENT` (Step H success), `COPILOT_TIMEOUT` (report and stop), zero unresolved threads in cycle 2+ (Step H success), or the 20-cycle safety limit. Reporting back to the user mid-loop is forbidden — the user expects an autopilot, not a status update every cycle.

### Cycle Step H: Report

When the loop exits (zero unresolved threads remain after a Copilot review), summarize:

- Total cycles completed
- Total threads across all cycles, broken down **by author group** (human reviewers vs Copilot) and by classification (valid / invalid / partial)
- Total **global comments** addressed (issue comments + review summary bodies), by author
- Total files modified
- CI status
- Final state: "All reviewer threads resolved, all actionable global comments addressed, and Copilot returned 0 new comments — CR is clean"

## Safety Limits

- **Max 20 cycles.** If after 20 cycles Copilot still generates new comments, stop and report the situation to the user. This likely means a systemic issue (e.g., Copilot keeps flagging the same pattern in different files).
- **Track repeated patterns.** If Copilot keeps raising the same type of comment (e.g., "blocks all implementation" in yet another file), note this in the report. After 3 cycles of the same pattern, search the entire CR diff for remaining instances and fix them all at once instead of one-by-one.
