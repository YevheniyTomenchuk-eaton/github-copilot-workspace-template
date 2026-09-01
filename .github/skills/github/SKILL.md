---
name: github
description: "GitHub CLI and API patterns for PR workflows, review threads, CI checks, and Copilot re-review. Covers: gh CLI prerequisites, authentication, repository identification, GraphQL queries/mutations for review threads, REST API for reviews and reviewers, Copilot review polling, git safety rules, and PowerShell pitfalls. Use when: any prompt or skill needs to interact with GitHub — shipping PRs, fixing review comments, requesting Copilot reviews, posting comments, checking CI, or cloning repos."
---

# GitHub Skill

## When to Use

When performing any GitHub operation via `gh` CLI or GitHub API:
- Shipping changes (commit, push, PR creation)
- Fetching or resolving PR review threads
- Posting PR comments or reviews
- Requesting Copilot code review
- Checking CI status
- Cloning or refreshing repositories
- Installing or authenticating `gh` CLI

## 1. Prerequisites — GitHub CLI

### Check if `gh` is installed

```powershell
$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
if ($null -ne $ghCommand) {
    $ghVersion = gh --version
    Write-Host "gh CLI found: $($ghVersion | Select-Object -First 1)"
} else {
    Write-Host "gh CLI NOT found — installing..."
}
```

### Install `gh` CLI (if missing)

```powershell
winget install --id GitHub.cli --accept-source-agreements --accept-package-agreements
```

After install, refresh PATH in the current session:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
gh --version
```

### Check authentication

```powershell
gh auth status 2>&1
```

If not logged in:

```powershell
gh auth login --hostname github.com --git-protocol https --web
```

This opens a browser window. Tell the user to complete authentication. Wait for exit code 0, then proceed.

### Verify repository access

```powershell
gh repo view <OWNER>/<REPO> --json name --jq .name 2>&1
```

If this fails, the user may not have access. Stop and inform them.

## 2. Repository Identification

Get owner and repo name for API calls. Two approaches depending on context:

### From current directory (when already inside a git repo)

```powershell
$nameWithOwner = gh repo view --json nameWithOwner --jq ".nameWithOwner"
$owner = $nameWithOwner.Split('/')[0]
$repo = $nameWithOwner.Split('/')[1]
```

### From user input

The user may specify `<OWNER>/<REPO>` directly. Split on `/` to get the two values.

## 3. PR Identification

### Check if current branch has a PR

```powershell
gh pr view --json number,url,state 2>&1
```

Returns PR metadata if one exists, or error text if not.

### Find PR by branch name

```powershell
gh pr view <NUMBER> --repo <OWNER>/<REPO> --json number,title,url,author,headRefName,baseRefName
```

Or search by branch:

```powershell
gh pr list --repo <OWNER>/<REPO> --head <BRANCH> --state open --json number,title,url,author,headRefName,baseRefName
```

### Create a PR

Author the body per §3 (Posting body text safely) — a single-quoted here-string written to a UTF-8 (no BOM) file — and post with `--body-file`:

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$body = @'
<multi-line markdown body>
'@
[System.IO.File]::WriteAllText("$env:TEMP\pr-body.md", $body, $utf8NoBom)
gh pr create --base main --head <current-branch> --title "<title>" --body-file "$env:TEMP\pr-body.md"
```

**Never** use inline `--body "..."` or a double-quoted here-string (`@"..."@`) — PowerShell mangles backticks (`` `n ``, `` `format` ``) and a phantom-failed interactive paste can post a duplicate. The `--body-file` approach sidesteps both.

### CRITICAL: Posting body text safely (charset + duplicates)

Any time you post free-form text to GitHub — a PR/issue comment (`gh pr comment`, `gh issue comment`), a review-thread reply, or a PR body — the text **must** travel through a file, never through an inline PowerShell string. Two failures happen otherwise and have already corrupted real PRs:

1. **Backtick escape corruption (mojibake).** In a double-quoted string or a double-quoted here-string (`@"..."@`), PowerShell interprets backtick sequences. `` `format` `` becomes a form-feed character + `ormat`; `` `n `` `` `t `` `` `r `` `` `0 `` `` `b `` `` `a `` all vanish or turn into control characters. Markdown is full of backticks, so inline bodies get silently mangled.
2. **Phantom duplicates.** Pasting a multi-line here-string into the interactive terminal can appear to fail (truncated output, no prompt return) while the command actually succeeded — leading you to retry and post a **second** copy.

**Mandatory pattern — write the body to a UTF-8 file, then pass it by reference:**

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$body = @'
Multi-line **markdown** with `backticks`, `format`, `continuationToken`, em-dashes — all safe here.
Single-quoted here-string: PowerShell performs ZERO escape interpretation.
'@
[System.IO.File]::WriteAllText("$env:TEMP\gh-body.md", $body, $utf8NoBom)

$url = gh pr comment <NUMBER> --body-file "$env:TEMP\gh-body.md"
Write-Output "POSTED_OK=$url"
# issue comment:        $url = gh issue comment <NUMBER> --body-file "$env:TEMP\gh-body.md"; Write-Output "POSTED_OK=$url"
# PR create:            $url = gh pr create ... --body-file "$env:TEMP\gh-body.md"; Write-Output "POSTED_OK=$url"
```

`gh pr comment` / `gh issue comment` / `gh pr create` print the created object's URL to stdout on success. **Always capture it and echo a `POSTED_OK=<url>` marker as the last line.** The marker makes the result unambiguous in a single snapshot — there is then never a reason to call the output "unclear" and re-verify. The garbled-echo trap (a multi-line here-string echoes a fragment like `8Encoding $false`, which *looks* like a failure but is just the terminal echoing the script) is exactly why the marker is mandatory: judge success by the presence of `POSTED_OK=`, not by how the echoed command looks.

For GraphQL mutations (review-thread replies), build the **full request payload** (query + variables) as one JSON object and pass it with `--input`, so no shell quoting touches the body. **Do not** combine `-f query=...` with `--input` — `gh api graphql --input` expects the entire `{query, variables}` body in the file and ignores/rejects a separate `-f query`:

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$mutation = 'mutation($subjectId: ID!, $body: String!) { addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $subjectId, body: $body}) { comment { id } } }'
$payload = @{ query = $mutation; variables = @{ subjectId = "<THREAD_ID>"; body = $body } } | ConvertTo-Json -Compress -Depth 5
[System.IO.File]::WriteAllText("$env:TEMP\gh-reply.json", $payload, $utf8NoBom)
$resp = gh api graphql --input "$env:TEMP\gh-reply.json" | ConvertFrom-Json
# Confirm: $resp.data.addPullRequestReviewThreadReply.comment.id is non-null
```

**Rules — no exceptions:**

- **Always** author body text in a **single-quoted** here-string (`@'...'@`) — never `@"..."@`, never a double-quoted inline string.
- **Always** write to a file with `New-Object System.Text.UTF8Encoding $false` (UTF-8 **without BOM**) and post with `--body-file` / `--input`.
- **Never** paste a multi-line here-string directly into the interactive terminal. Put it in a `.ps1` under `$env:TEMP` (or another explicitly scratch/temp location) and run via `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File`, or write the file in one non-interactive step. Keep scratch scripts out of the tracked repo — use `$env:TEMP` or a gitignored folder.
- **Always** capture the `gh` return value and echo `POSTED_OK=<url>` as the final line. Treat the presence of that marker — **not** the appearance of the echoed command — as the success signal. A garbled command echo (e.g. a stray `8Encoding $false` fragment) is the terminal echoing your multi-line script, never a failure. Do **not** label such output "unclear" and re-verify; that wastes a turn. If (and only if) the `POSTED_OK=` line is genuinely absent, **read** the comments to check — never re-run the post.
- **Before posting**, confirm the target has no existing copy; **after posting**, verify exactly one comment exists. If a post command's output is unclear, **read** the comments (do not re-run the post) — see the non-idempotency rule below.
- When building per-item bodies in a loop, reference hashtable fields with subexpressions: `-f "body=$($t.msg)"`, never `-f body=$t.msg` (the latter passes the stringified hashtable).

## 4. GraphQL API — Review Threads

> **Prefer the scripts** in [`.github/scripts/github/`](../../scripts/github/README.md) — they encapsulate the pagination, charset, and idempotency rules below so you never reconstruct a brittle inline mutation. The raw mechanics are documented after each script for reference and debugging.

### Fetch all review threads (MANDATORY pagination)

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/fetch-review-threads.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER>
# add -UnresolvedOnly to write only unresolved threads; -OutFile <path> to choose the JSON location
```

The script paginates, asserts `fetched == totalCount`, and writes the thread array to a UTF-8 JSON file. It prints `TOTAL_COUNT`, `FETCHED_COUNT`, `UNRESOLVED_COUNT`, and `OUT_FILE` — read the `OUT_FILE` JSON to inspect thread `id`, `isResolved`, and `comments`.

Why a script: GraphQL `reviewThreads(first: 100)` returns **at most 100 threads per page**; PRs with more silently drop the rest. The script paginates with `pageInfo.hasNextPage` + `endCursor` and never uses `--jq` (empty `--jq` output hides query failures rather than meaning "no threads").

- `id` on thread nodes = GraphQL ID (needed for mutations)
- `databaseId` on comment nodes = REST API numeric ID
- `totalCount` includes resolved threads — the script throws if `fetched != totalCount`

Each thread carries a lightweight `comments(first: 10)` window plus `comments.totalCount`, so the anchor (oldest comment = `comments[0]`) and early context are always present without pulling huge histories. When a thread has **more** comments than that window, the script prints a `COMMENTS_TRUNCATED=<n>` line listing those thread ids — fetch a specific thread's complete comment history **on demand** with the next script.

### Fetch one thread's full comment history (on demand)

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/fetch-thread-comments.ps1" `
  -ThreadId "<THREAD_ID>"
# -OutFile <path> to choose the JSON location
```

Use this only for threads flagged under `COMMENTS_TRUNCATED` (>10 comments). It paginates the single thread's comments with `pageInfo.hasNextPage` + `endCursor`, asserts `fetched == totalCount`, and writes the full comment array to a UTF-8 JSON file. It prints `THREAD_ID`, `TOTAL_COUNT`, `FETCHED_COUNT`, and `OUT_FILE`. This keeps the bulk fetch light while still letting you read every comment on a busy thread when you actually need it.

### CRITICAL: Fetch PR-level (global) comments — they are NOT review threads

Review threads (inline file comments) are only **one of three** places a reviewer leaves feedback. The other two are **PR-level** and have **no resolve affordance**, so a thread-only fetch silently misses them:

| Surface | Where it appears | API | Resolvable? |
|---|---|---|---|
| **Review threads** | Inline, anchored to a file + line | GraphQL `reviewThreads` (`fetch-review-threads.ps1`) | ✅ Yes — reply + resolve |
| **Issue comments** | The PR "Conversation" timeline | REST `.../issues/<pr>/comments` | ❌ No — reply only |
| **Review summary bodies** | The top-level prose typed when submitting a review | REST `.../pulls/<pr>/reviews` (non-empty `.body`) | ❌ No — reply only |

Humans frequently leave their **most important** guidance as a single global comment with **no inline threads at all** — "need fixes", "use the ADO template here", a paragraph of direction. A workflow that only walks `reviewThreads` will declare the CR clean while a substantive instruction sits unread. Copilot also emits a review summary body on every pass; a summary that generated **zero** inline comments is itself the convergence signal. Either way, global comments must be **read and addressed** even though they cannot be resolved like a thread.

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/fetch-pr-comments.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER>
# add -Since "<ISO8601>" to keep only comments newer than a timestamp (how a loop finds NEW global
#   comments per cycle — global comments have no resolved flag to track state); -OutFile <path> to choose location
```

The script paginates BOTH REST surfaces with `--paginate --slurp` (plain `--paginate` concatenates `[..][..]`, which `ConvertFrom-Json` cannot parse), drops empty-body review summaries, and writes one UTF-8 JSON object `{ issueComments: [...], reviewSummaries: [...] }`. It prints `ISSUE_COMMENT_COUNT`, `REVIEW_SUMMARY_COUNT`, `TOTAL_GLOBAL_COUNT`, and `OUT_FILE` — read the `OUT_FILE` JSON to inspect each comment's `author`, `body`, `createdAt`/`submittedAt`, and `url`.

**Addressing a global comment:** there is no resolve, and you do **not** post a separate reply per comment. Make the requested change in the codebase, then handle the acknowledgement based on **who wrote it**:

- **Human global comment** → fold the acknowledgement into the **single global summary comment** you post once per pass (`gh pr comment <NUMBER> --body-file ...`, see §3): **@-tag the author** there and note what you changed in response. One consolidated summary, not a reply per comment — a human is waiting for the acknowledgement, and the summary is where they get it.
- **Copilot global comment** (`*copilot*` author) → **do NOT acknowledge at all.** Copilot's review summary body is convergence boilerplate ("## Pull request overview … generated N comments"); its *actionable* content is the inline threads it filed, which you handle as threads. Still **act** on anything concrete, but never tag it or mention it in the summary.

Either way, never invent a thread to resolve — global comments have no resolve API. (Inline review threads are different — those still get a per-thread reply + resolve as in §4.)

### Reply to a thread

Author the reply body per §3 (single-quoted here-string → UTF-8 no-BOM file), then:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/reply-to-thread.ps1" `
  -ThreadId "<THREAD_ID>" -BodyPath "$env:TEMP\reply.md"
```

The script builds the full GraphQL payload (query + variables) as one JSON object and posts it via `gh api graphql --input`, then verifies `comment.id` is non-null. It prints `COMMENT_ID=<id>` on success and throws otherwise — never combine `-f query=...` with `--input` yourself.

### Resolve a thread

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/resolve-thread.ps1" -ThreadId "<THREAD_ID>"
```

### Un-resolve a thread

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/resolve-thread.ps1" -ThreadId "<THREAD_ID>" -Unresolve
```

### CRITICAL: Reply and resolve/un-resolve as SEPARATE commands

Never combine reply + resolve in a single terminal command. Run them sequentially:

1. Post the reply → confirm success (response contains `comment.id`)
2. Then resolve or un-resolve the thread → confirm success

### CRITICAL: Mutations are NOT idempotent — never re-run to "check" output

If the reply/un-resolve/resolve command output is truncated or unclear:

- **NEVER** re-run the mutation command. Re-running posts a duplicate comment or toggles state twice.
- **Instead**, verify with a read-only query: re-fetch the thread's comments (§4 — Fetch all review threads) and check if your reply/state change is present.
- The same applies to review submission (§5): never re-run the review POST. Verify by listing reviews with `gh api repos/.../pulls/<N>/reviews --paginate`.

## 5. REST API — Reviews

### Submit a review with inline comments

```powershell
$commitSha = (git rev-parse HEAD).Trim()

$review = @{
    commit_id = $commitSha
    body = "<REVIEW_SUMMARY>"
    event = "REQUEST_CHANGES"   # or "APPROVE" or "COMMENT"
    comments = @(
        @{
            path = "<FILE_PATH>"
            position = <DIFF_POSITION>
            body = "<COMMENT_BODY>"
        }
    )
}

$json = $review | ConvertTo-Json -Depth 4 -Compress
[System.IO.File]::WriteAllText("$env:TEMP\pr-review.json", $json)
gh api repos/<OWNER>/<REPO>/pulls/<NUMBER>/reviews -X POST --input "$env:TEMP\pr-review.json" --jq ".id"
```

- `position` = line number in the diff (not the file line number)
- `event` values: `APPROVE`, `REQUEST_CHANGES`, `COMMENT`
- Use `[System.IO.File]::WriteAllText()` — never `Out-File` (adds BOM)

### Submit an APPROVE review (no inline comments)

```powershell
$commitSha = (git rev-parse HEAD).Trim()

$review = @{
    commit_id = $commitSha
    body = "<REVIEW_SUMMARY>"
    event = "APPROVE"
}

$json = $review | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText("$env:TEMP\pr-review.json", $json)
gh api repos/<OWNER>/<REPO>/pulls/<NUMBER>/reviews -X POST --input "$env:TEMP\pr-review.json" --jq ".id"
```

### List all reviews (with pagination)

**CRITICAL:** Always use `--paginate` — without it, the REST API returns only the first 30 reviews, silently hiding reviews beyond page 1.

```powershell
$reviews = gh api repos/<OWNER>/<REPO>/pulls/<NUMBER>/reviews --paginate | ConvertFrom-Json
```

### Post a PR-level comment

```powershell
gh pr comment <NUMBER> --body "<SUMMARY>"
```

## 6. REST API — Copilot Code Review

### Request Copilot re-review

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/request-copilot-review.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER>
```

The script requests `copilot-pull-request-reviewer[bot]` and reads back the pending reviewers to confirm, printing `COPILOT_REQUESTED=<true|false>`.

**CRITICAL — Three different Copilot identifiers exist. Using the wrong one silently fails:**

| Context | Login | Example |
|---|---|---|
| **Requesting review** | `copilot-pull-request-reviewer[bot]` | `-f 'reviewers[]=copilot-pull-request-reviewer[bot]'` |
| **Checking pending reviewers** | `Copilot` | `$_.login -like "*copilot*"` matches both |
| **Review author** (in review objects) | `copilot-pull-request-reviewer[bot]` | `$_.user.login -like "*copilot*"` |

Using `Copilot` (capital C, no bot suffix) in the request silently returns HTTP 200 with an empty `requested_reviewers` list — no error, no reviewer added.

### Poll for Copilot review completion

Record the Copilot review count **before** requesting (from the `fetch-review-threads` / reviews data), then poll:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/poll-copilot-review.ps1" `
  -Owner "<OWNER>" -Repo "<REPO>" -Pr <NUMBER> -ReviewCountBefore <REVIEW_COUNT_BEFORE> -Quiet
```

Run with `mode=sync` and a generous `timeout` (≥ 700000 ms) — larger than the script's `-TimeoutMinutes` (default 10) so the loop returns before the tool timeout fires. The agent's turn blocks until the loop exits with one of the sentinel strings below — no `get_terminal_output` polling needed, and **no tokens are spent during the wait** because the model generates nothing while the terminal call is blocked. **Never run this `mode=async`** — async hands control back early, and each re-entry to re-check is a billable model turn.

Pass `-Quiet` to suppress the per-15s `WAITING:` progress lines so only the final sentinel returns to context (the progress chatter would otherwise be fed back into the model on each turn).

Exit conditions:
- **`COPILOT_DONE`**: New review submitted — proceed with next action
- **`COPILOT_SILENT`**: Copilot left pending list without a new review — likely clean pass
- **`COPILOT_TIMEOUT`**: Copilot is stuck — report to user and stop

**Note:** `Start-Sleep` is allowed inside this polling script even under sync mode — the agent-level prohibition on `Start-Sleep` applies only to standalone wait commands, not to the body of a long-running poll that is itself the unit of work.

**Race condition:** If you check pending reviewers immediately after requesting, Copilot may not have been added yet, causing a false "not pending" result. The polling script handles this by requiring 2 minutes before trusting a "not pending" signal.

## 7. CI Status

### Check PR checks without waiting

Use the helper script — it queries the PR's checks **once**, never polls or waits for in-progress runs, and surfaces only completed failures with their run ids:

```powershell
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File ".github/scripts/github/check-pipeline-status.ps1" `
  -Repo "<OWNER>/<REPO>" -Pr <NUMBER>
```

It prints `PIPELINE_STATUS=<failing|pending|passing|none>`, `FAILING_COUNT`, `PENDING_COUNT`, and one `FAILURE=<name>`<TAB>`<runId>`<TAB>`<link>` line per failed check. A `pending` pipeline (queued / running) must **never** block a workflow — re-check it later rather than waiting.

The raw query, when you need it directly, is `gh pr checks --json name,state,bucket,link`. The `conclusion` field does not exist — use `state` (values: `SUCCESS`, `FAILURE`, `PENDING`, `QUEUED`) or the cleaner `bucket` (`pass`, `fail`, `pending`, `skipping`, `cancel`).

### Get failed run logs

Use the `runId` from a `FAILURE=` line (or extract the number from a check link's `.../runs/12345678/...`):

```powershell
gh run view <RUN_ID> --log-failed
```

## 8. Git Safety Rules

### Destructive operations — NEVER without permission

These commands are **forbidden** unless the user explicitly requests them and you explain what will be lost:

| Command | Why it's dangerous |
|---|---|
| `git stash` | Hides uncommitted work — easy to lose |
| `git stash drop` / `git stash clear` | Permanently deletes stashed changes |
| `git clean -fd` / `git clean -f` | Permanently deletes untracked files |
| `git checkout -- .` / `git restore .` | Discards all uncommitted changes |
| `git reset --hard` | Destroys uncommitted work and rewrites history |
| `git checkout <other-branch>` with dirty working tree | May refuse or silently drop changes |

**Key principle:** When in doubt, commit and push what you have. A messy commit on a feature branch is better than lost work.

### Branch rules

- NEVER push to `main` directly — always create a PR
- NEVER use `--force` push (except `--force-with-lease` on merge branches after amending a merge commit — see merge workflow)
- NEVER switch branches with uncommitted work — commit and push first
- NEVER create a new branch when there's already an active feature branch with an open PR

### Feature branch naming

```
ai/<short-description>
```

Lowercase, kebab-case, max 5 words.

## 9. PowerShell Pitfalls

These have caused real failures. Follow them exactly:

| Pitfall | Rule |
|---|---|
| `--jq` on GraphQL | Never use — empty output means silent failure, not "no results" |
| `reviewThreads(first: 100)` without pagination | Always paginate with `pageInfo.hasNextPage` + `endCursor`; assert `fetched == totalCount` |
| `--paginate` on review lists | Always use — without it, only first 30 reviews returned |
| `\n` in `gh pr create --body` | Use PowerShell backtick-n (`` `n ``) instead — `\n` renders as literal text |
| `Out-File` for JSON payloads | Use `[System.IO.File]::WriteAllText()` — `Out-File` adds BOM that corrupts JSON |
| Chaining git commands with `;` + `Select-Object -Last N` | Don't — masks errors and produces ambiguous exit codes. Run each command separately |
| Reply + resolve in one command | Run as separate terminal commands — combined calls fail silently |
| Multi-line comment bodies | Build in PowerShell variable with backtick-n, convert with `ConvertTo-Json -Compress`, write to file, post with `--input <file>` |

## 10. Clone / Refresh Pattern

For cloning external repos for review or analysis:

### Refresh existing clone (faster — only for clean checkouts)

```powershell
cd <CLONE_DIR>
git status --porcelain  # must be empty — if not, re-clone instead
git fetch origin <BRANCH> <BASE> --no-tags
git checkout <BRANCH>
git reset --hard origin/<BRANCH>
```

### Fresh clone

Run each command **separately** — do not chain with `;`:

```powershell
git clone https://github.com/<OWNER>/<REPO>.git <CLONE_DIR> --no-tags --single-branch --branch <BRANCH>
```

```powershell
cd <CLONE_DIR>
```

```powershell
git fetch origin <BASE>:refs/remotes/origin/<BASE>
```

After each step, verify it succeeded before moving on.
