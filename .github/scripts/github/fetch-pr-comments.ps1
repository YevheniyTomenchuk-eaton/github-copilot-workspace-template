<#
.SYNOPSIS
Fetch ALL PR-level (global) comments for a pull request — issue comments AND review summary bodies —
paginate completely, and write them to a JSON file.

.DESCRIPTION
Review THREADS (inline file comments) are only one of three places a reviewer can leave feedback. The
other two are PR-LEVEL and have no "resolve" affordance, so a thread-only fetch silently misses them:

  1. Issue comments      — the PR "Conversation" timeline (gh api .../issues/<pr>/comments).
  2. Review summary bodies — the top-level body a reviewer types when submitting a review, separate from
                             any inline comments (gh api .../pulls/<pr>/reviews, the non-empty .body).

Humans frequently leave their most important guidance as a single global comment with NO inline threads
("need fixes", "use the ado template here", a paragraph of direction). Copilot also emits a review
summary body every pass; a summary that generated zero inline comments is itself the convergence signal.
Either way these must be READ and ADDRESSED even though they cannot be resolved like a thread.

This script paginates BOTH REST surfaces with `--paginate --slurp` (robust across multi-page PRs — plain
`--paginate` concatenates `[..][..]` which ConvertFrom-Json cannot parse), flattens the pages, and writes
a single UTF-8 (no BOM) JSON object so the caller can read structured data without re-querying.

Use `-Since <ISO8601>` to keep only comments created/submitted strictly after a timestamp — this is how an
autopilot loop finds the global comments that arrived since the previous cycle without re-addressing old
ones (global comments have no resolved flag to track state). Empty-body review summaries are always
dropped — only summaries with actual prose are returned.

It NEVER uses `--jq` (empty `--jq` output hides query failures rather than meaning "no comments").

.PARAMETER Owner
Repository owner (e.g. etn-electrical).

.PARAMETER Repo
Repository name (e.g. my-repo).

.PARAMETER Pr
Pull request number.

.PARAMETER Since
Optional ISO8601 timestamp (e.g. 2026-06-12T04:00:00Z). Only comments strictly newer than this are kept.

.PARAMETER OutFile
Optional. Path to write the JSON object. Defaults to a temp file; the path is echoed as OUT_FILE=.

.OUTPUTS
ISSUE_COMMENT_COUNT=<n>
REVIEW_SUMMARY_COUNT=<n>
TOTAL_GLOBAL_COUNT=<n>
OUT_FILE=<path>
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $true)]
    [int]$Pr,

    [string]$Since,

    [string]$OutFile
)

$ErrorActionPreference = 'Stop'

$sinceDate = $null
if ($Since) {
    $sinceDate = [DateTimeOffset]::Parse($Since, [System.Globalization.CultureInfo]::InvariantCulture)
}

function Get-PaginatedRest {
    param([string]$Path)

    $raw = gh api $Path --paginate --slurp 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "gh api $Path failed (exit $LASTEXITCODE): $raw"
    }
    if ([string]::IsNullOrWhiteSpace($raw)) {
        throw "gh api $Path returned empty output (silent failure?)"
    }

    $pages = $raw | ConvertFrom-Json
    $items = @()
    foreach ($page in $pages) {
        if ($null -ne $page) {
            $items += $page
        }
    }
    return $items
}

$issueRaw = Get-PaginatedRest -Path "repos/$Owner/$Repo/issues/$Pr/comments"
$reviewRaw = Get-PaginatedRest -Path "repos/$Owner/$Repo/pulls/$Pr/reviews"

$issueComments = @()
foreach ($c in $issueRaw) {
    if ($sinceDate -and [DateTimeOffset]::Parse($c.created_at, [System.Globalization.CultureInfo]::InvariantCulture) -le $sinceDate) {
        continue
    }
    $issueComments += [PSCustomObject]@{
        id        = $c.id
        author    = $c.user.login
        createdAt = $c.created_at
        body      = $c.body
        url       = $c.html_url
    }
}

$reviewSummaries = @()
foreach ($r in $reviewRaw) {
    if ([string]::IsNullOrWhiteSpace($r.body)) {
        continue
    }
    if ($sinceDate -and $r.submitted_at -and [DateTimeOffset]::Parse($r.submitted_at, [System.Globalization.CultureInfo]::InvariantCulture) -le $sinceDate) {
        continue
    }
    $reviewSummaries += [PSCustomObject]@{
        id          = $r.id
        author      = $r.user.login
        submittedAt = $r.submitted_at
        state       = $r.state
        body        = $r.body
        url         = $r.html_url
    }
}

if (-not $OutFile) {
    $OutFile = Join-Path $env:TEMP ("gh-global-pr$Pr-" + [System.Guid]::NewGuid().ToString('N') + ".json")
}

$outDir = Split-Path -Parent $OutFile
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$result = [PSCustomObject]@{
    issueComments   = @($issueComments)
    reviewSummaries = @($reviewSummaries)
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$json = ConvertTo-Json -InputObject $result -Depth 8
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)

"ISSUE_COMMENT_COUNT=$($issueComments.Count)"
"REVIEW_SUMMARY_COUNT=$($reviewSummaries.Count)"
"TOTAL_GLOBAL_COUNT=$($issueComments.Count + $reviewSummaries.Count)"
"OUT_FILE=$OutFile"
