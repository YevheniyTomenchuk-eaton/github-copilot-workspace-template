#requires -Version 5.1
<#
.SYNOPSIS
    Run a single, non-breaking foreground countdown loop for a fixed number of minutes,
    printing one tick line per second.
.DESCRIPTION
    Backs the workspace.demo.steering-and-queueing demo prompt. Its only purpose is to
    produce a steady stream of terminal output while a prompt is running, so the
    presenter can demonstrate Steering, queued messages, and Stop. It changes nothing
    on disk and is safe to cancel at any moment.
.PARAMETER Minutes
    How many minutes the loop should run.
.OUTPUTS
    One "[tick NNNN] loop running — Ns remaining" line per second, then a completion line.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][int]$Minutes
)

$end = (Get-Date).AddMinutes($Minutes)
$tick = 0
while ((Get-Date) -lt $end) {
    $tick++
    $remaining = [int]([Math]::Ceiling(($end - (Get-Date)).TotalSeconds))
    Write-Host ("[tick {0:0000}] loop running — {1,4}s remaining" -f $tick, $remaining)
    Start-Sleep -Seconds 1
}
Write-Host ("Loop complete — ran for {0} minute(s), printed {1} ticks." -f $Minutes, $tick)
