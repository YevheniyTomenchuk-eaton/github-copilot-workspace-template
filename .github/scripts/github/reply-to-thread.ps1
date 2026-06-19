<#
.SYNOPSIS
Post a reply to a GitHub pull-request review thread, safely (no charset corruption, no duplicates).

.DESCRIPTION
Reads the reply body from a UTF-8 file, builds the full GraphQL payload (query + variables) as one
JSON object, and posts it via `gh api graphql --input`. This is the ONLY reliable way to post markdown
bodies that contain backticks, em-dashes, or other characters that PowerShell mangles in inline strings.

The mutation is NOT idempotent. If this script throws after a partial run, do NOT blindly re-run it —
re-fetch the thread (see fetch-review-threads.ps1) and check whether your reply already posted.

.PARAMETER ThreadId
The GraphQL node ID of the review thread (e.g. PRRT_kwDO...). Get it from fetch-review-threads.ps1.

.PARAMETER BodyPath
Path to a UTF-8 file containing the reply markdown. Author it as a single-quoted here-string and write
it with [System.IO.File]::WriteAllText(..., (New-Object System.Text.UTF8Encoding $false)).

.OUTPUTS
COMMENT_ID=<node id>   on success (throws on failure).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ThreadId,

    [Parameter(Mandatory = $true)]
    [string]$BodyPath
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $BodyPath)) {
    throw "Body file not found: $BodyPath"
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$resolved = (Resolve-Path -LiteralPath $BodyPath).Path
$body = [System.IO.File]::ReadAllText($resolved, $utf8NoBom)

if ([string]::IsNullOrWhiteSpace($body)) {
    throw "Body file is empty: $BodyPath"
}

$mutation = 'mutation($subjectId: ID!, $body: String!) { addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $subjectId, body: $body}) { comment { id } } }'
$payload = @{ query = $mutation; variables = @{ subjectId = $ThreadId; body = $body } } | ConvertTo-Json -Compress -Depth 5

$payloadFile = Join-Path $env:TEMP ("gh-reply-" + [System.Guid]::NewGuid().ToString('N') + ".json")
[System.IO.File]::WriteAllText($payloadFile, $payload, $utf8NoBom)

try {
    $respRaw = gh api graphql --input $payloadFile
    if ($LASTEXITCODE -ne 0) {
        throw "gh api graphql failed (exit $LASTEXITCODE): $respRaw"
    }
}
finally {
    Remove-Item -LiteralPath $payloadFile -Force -ErrorAction SilentlyContinue
}

$resp = $respRaw | ConvertFrom-Json
$commentId = $resp.data.addPullRequestReviewThreadReply.comment.id

if ([string]::IsNullOrWhiteSpace($commentId)) {
    throw "Reply failed - no comment id returned. Response: $respRaw"
}

"COMMENT_ID=$commentId"
