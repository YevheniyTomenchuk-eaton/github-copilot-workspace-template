<#
.SYNOPSIS
Fetch ALL review threads for a pull request (paginated), assert completeness, and write them to a JSON file.

.DESCRIPTION
GraphQL reviewThreads(first: 100) returns at most 100 threads per page. This script paginates with
pageInfo.hasNextPage + endCursor until every thread is fetched, then asserts fetched == totalCount so a
silent truncation can never pass unnoticed. It NEVER uses --jq (empty --jq output hides query failures).

Each thread carries a lightweight first: 10 comments window plus comments.totalCount, so the anchor
(oldest comment, comments[0]) and early context are always present without pulling huge histories.
Threads whose totalCount exceeds the fetched window are listed under COMMENTS_TRUNCATED; fetch a
specific thread's complete comment history ON DEMAND with fetch-thread-comments.ps1 -ThreadId <id>.

The full thread array is written to a UTF-8 (no BOM) JSON file so the caller can read structured data
without re-running the query. Counts are emitted to stdout as KEY=value lines.

.PARAMETER Owner
Repository owner (e.g. etn-electrical).

.PARAMETER Repo
Repository name (e.g. my-repo).

.PARAMETER Pr
Pull request number.

.PARAMETER OutFile
Optional. Path to write the JSON array. Defaults to a temp file; the path is echoed as OUT_FILE=.

.PARAMETER UnresolvedOnly
Switch. When set, the written JSON contains only unresolved threads (counts still reflect totals).

.OUTPUTS
TOTAL_COUNT=<n>
FETCHED_COUNT=<n>
UNRESOLVED_COUNT=<n>
OUT_FILE=<path>
COMMENTS_TRUNCATED=<n>   (only when one or more threads have more comments than the fetched window)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $true)]
    [int]$Pr,

    [string]$OutFile,

    [switch]$UnresolvedOnly
)

$ErrorActionPreference = 'Stop'

$query = @'
query($owner: String!, $name: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $cursor) {
        totalCount
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          comments(first: 10) {
            totalCount
            pageInfo { hasNextPage endCursor }
            nodes { id, body, path, line, createdAt, author { login }, databaseId }
          }
        }
      }
    }
  }
}
'@

$cursor = $null
$allThreads = @()
$totalCount = $null

do {
    if ($cursor) {
        $respRaw = gh api graphql -f query=$query -f owner=$Owner -f name=$Repo -F pr=$Pr -f cursor=$cursor
    }
    else {
        $respRaw = gh api graphql -f query=$query -f owner=$Owner -f name=$Repo -F pr=$Pr
    }
    if ($LASTEXITCODE -ne 0) {
        throw "gh api graphql failed (exit $LASTEXITCODE): $respRaw"
    }

    $resp = $respRaw | ConvertFrom-Json
    $page = $resp.data.repository.pullRequest.reviewThreads
    if ($null -eq $page) {
        throw "Query returned no reviewThreads (silent failure?). Response: $respRaw"
    }

    if ($null -eq $totalCount) { $totalCount = $page.totalCount }
    $allThreads += $page.nodes
    $cursor = $page.pageInfo.endCursor
} while ($page.pageInfo.hasNextPage)

if ($allThreads.Count -ne $totalCount) {
    throw "Pagination incomplete: fetched $($allThreads.Count) of $totalCount threads"
}

$unresolvedCount = @($allThreads | Where-Object { -not $_.isResolved }).Count

if ($UnresolvedOnly) {
    $result = @($allThreads | Where-Object { -not $_.isResolved })
}
else {
    $result = $allThreads
}

if (-not $OutFile) {
    $OutFile = Join-Path $env:TEMP ("gh-threads-pr$Pr-" + [System.Guid]::NewGuid().ToString('N') + ".json")
}

$outDir = Split-Path -Parent $OutFile
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$json = ConvertTo-Json -InputObject @($result) -Depth 8
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)

"TOTAL_COUNT=$totalCount"
"FETCHED_COUNT=$($allThreads.Count)"
"UNRESOLVED_COUNT=$unresolvedCount"
"OUT_FILE=$OutFile"

$truncated = @($allThreads | Where-Object { $_.comments.totalCount -gt $_.comments.nodes.Count })
if ($truncated.Count -gt 0) {
    "COMMENTS_TRUNCATED=$($truncated.Count)"
    "  (fetch a thread's full history on demand with fetch-thread-comments.ps1 -ThreadId <id>)"
    foreach ($th in $truncated) {
        "  THREAD $($th.id): showing $($th.comments.nodes.Count) of $($th.comments.totalCount) comments"
    }
}
