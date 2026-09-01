<#
.SYNOPSIS
Report a pull request's CI pipeline status WITHOUT waiting for in-progress runs.

.DESCRIPTION
Queries the PR's checks exactly once and classifies them by bucket. It never polls or blocks:
checks that are still queued / in-progress are reported as PENDING and are NOT treated as failures.
Only checks that have actually completed with a failing conclusion are surfaced as failures, each
with the originating workflow run id so the caller can pull the failed log and classify the cause.

This lets the fix-cr / autopilot prompts proceed past a pipeline that is merely still running and act
only on genuine red checks - a running pipeline must never block the loop.

.PARAMETER Pr
Pull request number.

.PARAMETER Repo
Optional `owner/name` slug. When omitted, gh infers the repo from the current clone.

.OUTPUTS
PIPELINE_STATUS=<failing|pending|passing|none>
FAILING_COUNT=<n>
PENDING_COUNT=<n>
FAILURE=<name>`t<runId>`t<link>   (one line per failed check; runId is empty when not derivable)

PIPELINE_STATUS semantics:
  failing  - at least one completed check failed (act on the FAILURE lines)
  pending  - no failures, but some checks are still queued/running or were cancelled (do NOT wait; re-check / rerun later)
  passing  - every check completed successfully
  none     - the PR has no checks configured
#>
[CmdletBinding()]
param(
    [int]$Pr = $(throw 'Required parameter -Pr was not provided.'),

    [string]$Repo
)

$ErrorActionPreference = 'Stop'

$repoArgs = @()
if ($Repo) {
    $repoArgs = @('--repo', $Repo)
}

$checksRaw = gh pr checks $Pr @repoArgs --json 'name,state,bucket,link' 2>&1
if ($LASTEXITCODE -ne 0) {
    # gh pr checks exits non-zero when checks are failing or pending; that is expected. Only a
    # missing-checks message means there is nothing to evaluate.
    if ($checksRaw -match 'no checks reported') {
        "PIPELINE_STATUS=none"
        "FAILING_COUNT=0"
        "PENDING_COUNT=0"
        return
    }
}

$checks = $null
try {
    $checks = $checksRaw | ConvertFrom-Json
}
catch {
    throw "Failed to parse gh pr checks output: $checksRaw"
}

if (-not $checks -or @($checks).Count -eq 0) {
    "PIPELINE_STATUS=none"
    "FAILING_COUNT=0"
    "PENDING_COUNT=0"
    return
}

$failing = @($checks | Where-Object { $_.bucket -eq 'fail' })
$pending = @($checks | Where-Object { $_.bucket -eq 'pending' -or $_.bucket -eq 'cancel' })

if ($failing.Count -gt 0) {
    "PIPELINE_STATUS=failing"
}
elseif ($pending.Count -gt 0) {
    "PIPELINE_STATUS=pending"
}
else {
    "PIPELINE_STATUS=passing"
}

"FAILING_COUNT=$($failing.Count)"
"PENDING_COUNT=$($pending.Count)"

foreach ($check in $failing) {
    $runId = ''
    if ($check.link -match '/runs/(\d+)') {
        $runId = $matches[1]
    }
    "FAILURE=$($check.name)`t$runId`t$($check.link)"
}
