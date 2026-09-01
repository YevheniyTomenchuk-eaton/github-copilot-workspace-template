<#
.SYNOPSIS
Request a Copilot re-review on a pull request and confirm Copilot is now a pending reviewer.

.DESCRIPTION
Requests review from copilot-pull-request-reviewer[bot] (the ONLY identifier that works for requesting -
"Copilot" silently returns HTTP 200 with an empty reviewer list), then reads back the pending reviewers
to confirm Copilot was actually added.

.PARAMETER Owner
Repository owner (e.g. etn-electrical).

.PARAMETER Repo
Repository name (e.g. my-repo).

.PARAMETER Pr
Pull request number.

.OUTPUTS
COPILOT_REQUESTED=<true|false>   (true = Copilot is a pending reviewer; throws on API failure).
#>
[CmdletBinding()]
param(
    [string]$Owner = $(throw 'Required parameter -Owner was not provided.'),

    [string]$Repo = $(throw 'Required parameter -Repo was not provided.'),

    [int]$Pr = $(throw 'Required parameter -Pr was not provided.')
)

$ErrorActionPreference = 'Stop'

# The POST response is authoritative: it returns the PR with the resulting requested_reviewers
# list. Checking it directly avoids the race where a separate read-back misses Copilot because it
# already moved from "requested" to actively reviewing. Match with a wildcard: the request login is
# 'copilot-pull-request-reviewer[bot]' but the API returns the reviewer as 'Copilot' - an exact-login
# check fails. A wrong identifier silently returns HTTP 200 with an empty reviewer list, so an empty
# match here is the genuine failure signal.
$postRaw = gh api "repos/$Owner/$Repo/pulls/$Pr/requested_reviewers" -X POST -f 'reviewers[]=copilot-pull-request-reviewer[bot]' 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Failed to request Copilot review (exit $LASTEXITCODE): $postRaw"
}

$post = $postRaw | ConvertFrom-Json
$copilotRequested = @($post.requested_reviewers | Where-Object { $_.login -like '*copilot*' }).Count -gt 0

if (-not $copilotRequested) {
    # Fallback: re-requesting a reviewer who is already pending can return a response without the
    # reviewer echoed back. Confirm via a direct read of the pending reviewers before reporting false.
    # A failed read-back must throw (per the script contract) so an auth/network error is never
    # silently reported as COPILOT_REQUESTED=false.
    $pendingRaw = gh api "repos/$Owner/$Repo/pulls/$Pr/requested_reviewers" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read back pending reviewers (exit $LASTEXITCODE): $pendingRaw"
    }
    $pending = $pendingRaw | ConvertFrom-Json
    $copilotRequested = @($pending.users | Where-Object { $_.login -like '*copilot*' }).Count -gt 0
}

"COPILOT_REQUESTED=$copilotRequested"
