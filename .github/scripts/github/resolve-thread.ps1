<#
.SYNOPSIS
Resolve (or un-resolve) a GitHub pull-request review thread.

.DESCRIPTION
Runs the resolveReviewThread / unresolveReviewThread GraphQL mutation. These mutations toggle state,
so they are effectively non-idempotent for un-resolve - never re-run blindly to "check" the result;
re-fetch the thread (fetch-review-threads.ps1) instead.

Always run this AFTER posting the reply (reply-to-thread.ps1), as a separate step.

.PARAMETER ThreadId
The GraphQL node ID of the review thread (e.g. PRRT_kwDO...).

.PARAMETER Unresolve
Switch. When set, un-resolves the thread instead of resolving it.

.OUTPUTS
IS_RESOLVED=<true|false>   (throws on failure).
#>
[CmdletBinding()]
param(
    [string]$ThreadId = $(throw 'Required parameter -ThreadId was not provided.'),

    [switch]$Unresolve
)

$ErrorActionPreference = 'Stop'

if ($Unresolve) {
    $mutation = 'mutation($threadId: ID!) { unresolveReviewThread(input: {threadId: $threadId}) { thread { isResolved } } }'
}
else {
    $mutation = 'mutation($threadId: ID!) { resolveReviewThread(input: {threadId: $threadId}) { thread { isResolved } } }'
}

$respRaw = gh api graphql -f query=$mutation -f threadId=$ThreadId
if ($LASTEXITCODE -ne 0) {
    throw "gh api graphql failed (exit $LASTEXITCODE): $respRaw"
}

$resp = $respRaw | ConvertFrom-Json
if ($Unresolve) {
    $isResolved = $resp.data.unresolveReviewThread.thread.isResolved
}
else {
    $isResolved = $resp.data.resolveReviewThread.thread.isResolved
}

if ($null -eq $isResolved) {
    throw "Mutation returned no thread state. Response: $respRaw"
}

"IS_RESOLVED=$isResolved"
