<#
.SYNOPSIS
Poll a pull request until Copilot submits a new review, leaves the pending list, or a timeout elapses.

.DESCRIPTION
Records nothing itself - the caller passes the Copilot review count captured BEFORE requesting the
re-review (request-copilot-review.ps1). This script then polls the reviews endpoint until the count
increases (COPILOT_DONE), Copilot drops off the pending list with no new review (COPILOT_SILENT, a
likely clean pass), or the timeout is reached (COPILOT_TIMEOUT).

Run this with run_in_terminal mode=sync and a timeout LARGER than -TimeoutMinutes (e.g. 700000 ms for
the default 10 minutes) so the agent turn blocks until a sentinel line is printed. Start-Sleep inside
this loop is intentional - it is the unit of work, not a standalone wait.

.PARAMETER Owner
Repository owner (e.g. etn-electrical).

.PARAMETER Repo
Repository name (e.g. my-repo).

.PARAMETER Pr
Pull request number.

.PARAMETER ReviewCountBefore
The number of Copilot reviews that existed BEFORE the re-review was requested.

.PARAMETER TimeoutMinutes
Maximum minutes to poll. Default 10.

.PARAMETER Quiet
Suppress the per-iteration WAITING and transient NETWORK_ERROR lines, emitting only the single
terminal sentinel. Use this when the caller blocks on the script with run_in_terminal mode=sync -
it keeps the returned output to one line so no progress chatter is fed back into the model's context.

.OUTPUTS
A WAITING line every 15s (unless -Quiet), then one terminal sentinel:
COPILOT_DONE: ... | COPILOT_SILENT: ... | COPILOT_TIMEOUT: ...
#>
[CmdletBinding()]
param(
    [string]$Owner = $(throw 'Required parameter -Owner was not provided.'),

    [string]$Repo = $(throw 'Required parameter -Repo was not provided.'),

    [int]$Pr = $(throw 'Required parameter -Pr was not provided.'),

    [int]$ReviewCountBefore = $(throw 'Required parameter -ReviewCountBefore was not provided.'),

    [int]$TimeoutMinutes = 10,

    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

function Write-Progress-Line {
    param([string]$Message)
    if (-not $Quiet) {
        $Message
    }
}

# Match Copilot with a wildcard: the request uses 'copilot-pull-request-reviewer[bot]' but the
# reviews and requested_reviewers APIs return the login as 'Copilot'. An exact-login check fails.
$startTime = Get-Date
while ($true) {
    $elapsed = (Get-Date) - $startTime
    if ($elapsed.TotalMinutes -ge $TimeoutMinutes) {
        "COPILOT_TIMEOUT: waited $TimeoutMinutes minutes, Copilot did not submit a review"
        break
    }

    $reviewsJson = gh api "repos/$Owner/$Repo/pulls/$Pr/reviews" --paginate 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Progress-Line "NETWORK_ERROR: $reviewsJson ... retrying"
        Start-Sleep -Seconds 15
        continue
    }
    $reviews = $reviewsJson | ConvertFrom-Json
    $copilotReviews = @($reviews | Where-Object { $_.user.login -like '*copilot*' })
    $reviewCountNow = $copilotReviews.Count
    if ($reviewCountNow -gt $ReviewCountBefore) {
        "COPILOT_DONE: Reviews before: $ReviewCountBefore, now: $reviewCountNow"
        break
    }

    try {
        $pendingJson = gh api "repos/$Owner/$Repo/pulls/$Pr/requested_reviewers" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Progress-Line "NETWORK_ERROR: $pendingJson ... retrying"
            Start-Sleep -Seconds 15
            continue
        }
        $pendingData = $pendingJson | ConvertFrom-Json
        $copilotPending = @($pendingData.users | Where-Object { $_.login -like '*copilot*' }).Count -gt 0
    }
    catch {
        Write-Progress-Line "NETWORK_ERROR: $_ ... retrying"
        Start-Sleep -Seconds 15
        continue
    }

    if (-not $copilotPending -and $elapsed.TotalMinutes -ge 2) {
        "COPILOT_SILENT: no longer pending and no new review (likely clean pass)"
        break
    }

    Write-Progress-Line "WAITING: $reviewCountNow reviews (need >$ReviewCountBefore), pending=$copilotPending... $(Get-Date -Format 'HH:mm:ss')"
    Start-Sleep -Seconds 15
}
