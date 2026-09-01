#requires -Version 5.1
<#
.SYNOPSIS
    Install or remove the temporary hooks-tour hook that wires every hook event to hook-tour.ps1.
.DESCRIPTION
    Backs the workspace.demo.hooks-tour demo skill. The hook JSON the demo needs is a *file shape*,
    so it lives here in the script (its one canonical home) instead of being pasted into the skill.
    The skill only calls this script.

    Default run: arms the tour (creates a fresh demo-hooks-tour marker folder in TEMP so hook-tour.ps1
    wakes up) and writes the temporary hook file .github/hooks/workspace.demo.hooks-tour.json that
    maps all ten events to hook-tour.ps1, passing the event name with -Event.

    With -Remove: deletes the temporary hook file and the marker folder, restoring the workspace to
    its starting state.
.PARAMETER Remove
    Remove the temporary hook and the arming marker folder instead of installing them.
.OUTPUTS
    Machine-readable KEY=value lines (INSTALLED / REMOVED / HOOK / LOG). Exit code 0.
#>
[CmdletBinding()]
param(
    [switch]$Remove
)

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..'))
$hookFile = Join-Path $repoRoot '.github/hooks/workspace.demo.hooks-tour.json'
$tourDir = Join-Path $env:TEMP 'demo-hooks-tour'

if ($Remove) {
    Remove-Item -LiteralPath $hookFile -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $tourDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $env:TEMP 'demo-chain.ready') -Force -ErrorAction SilentlyContinue
    Write-Output "REMOVED=1"
    Write-Output "HOOK=$hookFile"
    exit 0
}

Remove-Item -LiteralPath $tourDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $env:TEMP 'demo-chain.ready') -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $tourDir -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $tourDir 'armed') -Force | Out-Null

$events = @(
    'SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'PreCompact',
    'SubagentStart', 'SubagentStop', 'Stop', 'SessionEnd', 'ErrorOccurred'
)

$hooks = [ordered]@{}
foreach ($name in $events) {
    $hooks[$name] = @(
        [ordered]@{
            type    = 'command'
            command = "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/hook-tour.ps1 -Event $name"
            windows = "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .github\scripts\workspace\demo\hook-tour.ps1 -Event $name"
        }
    )
}

$json = [ordered]@{ hooks = $hooks } | ConvertTo-Json -Depth 6

$dir = Split-Path -Parent $hookFile
if (-not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
[System.IO.File]::WriteAllText($hookFile, $json, (New-Object System.Text.UTF8Encoding($false)))

Write-Output "INSTALLED=1"
Write-Output "HOOK=$hookFile"
Write-Output "LOG=$(Join-Path $tourDir 'events.log')"
exit 0
