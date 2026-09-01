#requires -Version 5.1
<#
.SYNOPSIS
    Simulated background work for the hooks-tour chaining step: waits, then writes a completion marker file.
.DESCRIPTION
    Backs the PostToolUse chaining step of the workspace.demo.hooks-tour demo skill. Run this in the
    background (async terminal) so the agent keeps working while it runs. After the delay it writes the
    marker file that the tour's PostToolUse hook (hook-tour.ps1) watches for. When the marker appears, the
    hook detects it on the agent's next tool call and chains the agent into a follow-up step it was never
    asked for. The marker content is the "result" the background work produced, which the hook hands back
    to the agent.
.PARAMETER DelaySeconds
    How long the simulated work runs before completing. Default 5.
.OUTPUTS
    Progress lines to the terminal, and a marker file at $env:TEMP\demo-chain.ready.
#>
[CmdletBinding()]
param(
    [int]$DelaySeconds = 5
)

$marker = Join-Path $env:TEMP 'demo-chain.ready'
Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue

Write-Host "Background work started $([char]0x2014) running for $DelaySeconds second(s)..."
Start-Sleep -Seconds $DelaySeconds

$result = "demo report generated at $(Get-Date -Format 'HH:mm:ss') with 3 sections"
[System.IO.File]::WriteAllText($marker, $result, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Background work complete $([char]0x2014) wrote marker '$marker'."
