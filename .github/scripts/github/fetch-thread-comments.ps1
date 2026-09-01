<#
.SYNOPSIS
Fetch the COMPLETE comment history of a single review thread, ON DEMAND, and write it to a JSON file.

.DESCRIPTION
fetch-review-threads.ps1 carries only a lightweight first: 10 comments window per thread to avoid
pulling huge histories for every thread. When a specific thread has more comments than that window
(it is listed under COMMENTS_TRUNCATED), call this script with that thread's id to drain ALL of its
comments via the comments connection cursor. It asserts fetched == totalCount so no comment is missed,
and NEVER uses --jq (empty --jq output hides query failures).

The full comment array is written to a UTF-8 (no BOM) JSON file. Counts are emitted as KEY=value lines.

.PARAMETER ThreadId
The GraphQL node id of the review thread (e.g. PRRT_kwDOQekFzs6Is2M7).

.PARAMETER OutFile
Optional. Path to write the JSON array. Defaults to a temp file; the path is echoed as OUT_FILE=.

.OUTPUTS
THREAD_ID=<id>
TOTAL_COUNT=<n>
FETCHED_COUNT=<n>
OUT_FILE=<path>
#>
[CmdletBinding()]
param(
    [string]$ThreadId = $(throw 'Required parameter -ThreadId was not provided.'),

    [string]$OutFile
)

$ErrorActionPreference = 'Stop'

$query = @'
query($threadId: ID!, $cursor: String) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $cursor) {
        totalCount
        pageInfo { hasNextPage endCursor }
        nodes { id, body, path, line, createdAt, author { login }, databaseId }
      }
    }
  }
}
'@

$cursor = $null
$allComments = @()
$totalCount = $null

do {
    if ($cursor) {
        $respRaw = gh api graphql -f query=$query -f threadId=$ThreadId -f cursor=$cursor
    }
    else {
        $respRaw = gh api graphql -f query=$query -f threadId=$ThreadId
    }
    if ($LASTEXITCODE -ne 0) {
        throw "gh api graphql failed (exit $LASTEXITCODE): $respRaw"
    }

    $resp = $respRaw | ConvertFrom-Json
    $page = $resp.data.node.comments
    if ($null -eq $page) {
        throw "Query returned no comments for thread $ThreadId (silent failure?). Response: $respRaw"
    }

    if ($null -eq $totalCount) { $totalCount = $page.totalCount }
    $allComments += $page.nodes
    $cursor = $page.pageInfo.endCursor
} while ($page.pageInfo.hasNextPage)

if ($allComments.Count -ne $totalCount) {
    throw "Comment pagination incomplete: fetched $($allComments.Count) of $totalCount comments"
}

if (-not $OutFile) {
    $OutFile = Join-Path $env:TEMP ("gh-thread-comments-" + [System.Guid]::NewGuid().ToString('N') + ".json")
}

$outDir = Split-Path -Parent $OutFile
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$json = ConvertTo-Json -InputObject @($allComments) -Depth 8
[System.IO.File]::WriteAllText($OutFile, $json, $utf8NoBom)

"THREAD_ID=$ThreadId"
"TOTAL_COUNT=$totalCount"
"FETCHED_COUNT=$($allComments.Count)"
"OUT_FILE=$OutFile"
