# GitHub helper scripts

Reusable PowerShell scripts for GitHub PR review and shipping workflows. They encapsulate the
pagination, charset, and idempotency rules that brittle inline `gh api graphql` snippets keep getting
wrong. The [`github` skill](../../skills/github/SKILL.md) and the `/ship` / `/fix-cr` /
`/fix-cr-autopilot` skills call these instead of reconstructing the sequences by hand.

Run each via `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/<script>.ps1" ...`.

## Shipping

`/ship` is script-driven: the preflight decides the single correct path, the others perform the
mechanical git/gh steps. Every script takes `-Base <branch>` (default `main`) for repos that ship
into something else.

| Script | Purpose | Key output |
|---|---|---|
| `ship-preflight.ps1` | Read-only. Detect branch, dirtiness, PR state and submodule drift, then pick exactly one path | `ACTION` (`stop-no-changes` / `commit-push` / `commit-push-pr` / `branch-commit-push-pr` / `squash-recovery`), `BRANCH`, `PR_STATE`, `SUBMODULE_CHANGES`, `STOP_REASON` |
| `commit-and-push.ps1` | Commit (optionally onto a new branch via `-NewBranch`) and push. Excludes submodule gitlink changes from the commit | `RESULT=pushed`, `BRANCH`, `SKIPPED_SUBMODULES`, `STOP_REASON` |
| `rebase-onto-base.ps1` | Squash-merge recovery — move work onto a fresh branch cut from `origin/<base>` by cherry-pick, non-destructively | `RESULT=rebased` / `conflicts`, `NEW_BRANCH`, `DIFF_FILE_COUNT`, `CONFLICT_FILES`, `CHERRY_REMAINING` |
| `create-pr.ps1` | Create the PR from a UTF-8 body file; idempotent — returns the existing open PR instead of a duplicate | `RESULT=created` / `already-exists`, `PR_URL` |
| `invoke-git-command.ps1` | Shared Git wrapper. The only script allowed to capture Git with `2>&1` — Windows PowerShell 5.1 turns ordinary Git stderr progress into `NativeCommandError` | `ExitCode`, `Output` |

## PR review

| Script | Purpose | Key output |
|---|---|---|
| `fetch-review-threads.ps1` | Fetch ALL review threads (paginated, asserts `fetched == totalCount`), write JSON to a file. Carries a lightweight `comments(first: 10)` window + `totalCount` per thread; flags threads with more under `COMMENTS_TRUNCATED` | `TOTAL_COUNT`, `FETCHED_COUNT`, `UNRESOLVED_COUNT`, `OUT_FILE`, `COMMENTS_TRUNCATED` |
| `fetch-thread-comments.ps1` | Fetch ONE thread's complete comment history on demand (paginated, asserts `fetched == totalCount`) — for threads flagged under `COMMENTS_TRUNCATED` | `THREAD_ID`, `TOTAL_COUNT`, `FETCHED_COUNT`, `OUT_FILE` |
| `fetch-pr-comments.ps1` | Fetch ALL PR-level (global) comments — issue comments + review summary bodies — that review-thread fetches miss (paginated with `--slurp`, drops empty summaries, `-Since` keeps only newer-than). Global comments have no resolve affordance — read & act; acknowledge human ones in the single PR summary comment, never invent a thread | `ISSUE_COMMENT_COUNT`, `REVIEW_SUMMARY_COUNT`, `TOTAL_GLOBAL_COUNT`, `OUT_FILE` |
| `reply-to-thread.ps1` | Post a reply to a review thread from a UTF-8 body file (full-payload `--input`, verifies `comment.id`) | `COMMENT_ID` |
| `resolve-thread.ps1` | Resolve (or `-Unresolve`) a review thread | `IS_RESOLVED` |
| `request-copilot-review.ps1` | Request a Copilot re-review and confirm it is pending | `COPILOT_REQUESTED` |
| `poll-copilot-review.ps1` | Block until Copilot submits a new review, drops off pending, or times out | `COPILOT_DONE` / `COPILOT_SILENT` / `COPILOT_TIMEOUT` |
| `check-pipeline-status.ps1` | Report the PR's CI status in a single query **without waiting** for in-progress runs — only completed failures are surfaced, with their run ids (`<runId>` is empty when not derivable — fall back to extracting it from `<link>`) | `PIPELINE_STATUS` (`failing`/`pending`/`passing`/`none`), `FAILING_COUNT`, `PENDING_COUNT`, `FAILURE=<name>\t<runId>\t<link>` |

## Conventions

- Author reply/comment bodies as a **single-quoted** here-string written to a UTF-8 (no BOM) file, then
  pass the file path to the script. Never inline markdown in a double-quoted string (backtick corruption).
- GraphQL mutations are **not idempotent** — never re-run a reply/resolve to "check" the result. Re-fetch
  with `fetch-review-threads.ps1` instead.
- Run `poll-copilot-review.ps1` with `mode=sync` and a `timeout` larger than its `-TimeoutMinutes`.

## Hard-won rules (do not relearn these)

- **Never round-trip a PR description through a captured PowerShell variable.** `$body = gh pr view N --json body --jq .body` captures multi-line output as a **string array**; passing it to `WriteAllText` joins the elements with spaces (`$OFS`), destroying every newline, and the non-UTF-8 console codepage mojibakes characters like `—`. To edit a PR body, author it fresh in a UTF-8 (no BOM) file and push with `gh pr edit N --body-file <file>` — that path never touches the console encoding.
- **Match Copilot with a wildcard, never an exact login.** The request POST uses `copilot-pull-request-reviewer[bot]`, but the `reviews` and `requested_reviewers` APIs return the login as `Copilot`. Detection must use `-like '*copilot*'`. An exact-login check produces a false `COPILOT_REQUESTED=false` even though the request succeeded.
- **Trust the POST response for request confirmation.** `request-copilot-review.ps1` reads `requested_reviewers` from the request POST response itself (authoritative), falling back to a direct read only if the echo is empty — this avoids the race where Copilot has already moved from "requested" to actively reviewing.
- **Review threads are not the whole story — fetch global comments too.** A reviewer's most important note is often a single PR-level comment (issue comment or review summary body) with **no inline thread**. `fetch-review-threads.ps1` cannot see those. Always also run `fetch-pr-comments.ps1`; a CR is not "clean" until those are addressed. Global comments have no resolve API. **Never post a separate reply per global comment.** Acknowledge **human** global comments in the **single PR-level summary comment** you post once per pass (`gh pr comment`) — @-tag the author there and note what changed. For a **Copilot** global comment (`*copilot*` author) act on anything concrete but **never acknowledge it**: its summary body is convergence boilerplate it never reads, and its real asks are the inline threads. Never fabricate a thread just to resolve it.
