#requires -Version 5.1
<#
.SYNOPSIS
    One generic hook handler that backs the workspace.demo.hooks-tour demo for EVERY hook event.
.DESCRIPTION
    Backs the workspace.demo.hooks-tour demo skill. The skill installs a single temporary hook
    file (.github/hooks/workspace.demo.hooks-tour.json) that maps every supported hook event to this
    one script, passing the event name with -Event. VS Code pipes the hook input JSON on stdin.

    The script is INERT unless the demo is "armed": the skill creates a marker directory in TEMP
    before the tour and removes it afterwards. While not armed the script returns {"continue": true}
    and does nothing, so even a stray hook can never affect real work.

    While armed, every event:
      * appends one line ("<timestamp> <Event> fired") to a shared tour log so the presenter can
        watch every event land, and
      * produces a single, one-shot VISIBLE effect the first time that event fires (tracked by a
        per-event .done marker), then stays quiet so the demo never spams the agent.

    Per-event visible effect (first fire only, while armed):
      PreToolUse      -> DENY the action if it carries the demo sentinel token (the headline block);
                         any other tool call is allowed untouched.
      PostToolUse     -> if a background-work marker (demo-chain.ready, left by chain-worker.ps1)
                         is present, CHAIN the agent into a follow-up step it was never asked for;
                         otherwise inject the one-shot banner naming the event.
      Stop            -> block the agent's stop exactly once so it continues to the wrap-up step,
                         guarded by stop_hook_active so it can never loop.
      everything else -> inject a short additionalContext banner naming the event that just fired
                         (SessionStart, UserPromptSubmit, PostToolUse, SubagentStart, SubagentStop,
                         PreCompact, SessionEnd, ErrorOccurred).
.PARAMETER Event
    The hook event name this invocation represents (e.g. PreToolUse, SessionStart).
.OUTPUTS
    A hook JSON object on stdout. Exit code 0 in all cases.
#>
[CmdletBinding()]
param(
    [string]$Event = $(throw 'Required parameter -Event was not provided.')
)

$sentinel = 'DEMO-TOUR-BLOCK'
$tourDir = Join-Path $env:TEMP 'demo-hooks-tour'
$armed = Join-Path $tourDir 'armed'
$logFile = Join-Path $tourDir 'events.log'

function Write-ContinueAndExit {
    '{"continue": true}'
    exit 0
}

function Write-JsonAndExit {
    param($Object)
    $Object | ConvertTo-Json -Depth 6 -Compress
    exit 0
}

try {
    $raw = [Console]::In.ReadToEnd()

    if (-not (Test-Path -LiteralPath $armed)) {
        Write-ContinueAndExit
    }

    $stamp = (Get-Date).ToString('HH:mm:ss')
    Add-Content -LiteralPath $logFile -Value "$stamp  $Event fired" -ErrorAction SilentlyContinue

    if ($Event -eq 'PreToolUse') {
        if ($raw -and $raw.Contains($sentinel)) {
            Write-JsonAndExit ([ordered]@{
                hookSpecificOutput = [ordered]@{
                    hookEventName            = 'PreToolUse'
                    permissionDecision       = 'deny'
                    permissionDecisionReason = "Blocked by the hooks-tour. This PreToolUse hook saw the sentinel token '$sentinel' and stopped the action before it ran. A hook decides BEFORE the tool executes - deterministically, no matter how the agent was asked."
                }
            })
        }
        Write-ContinueAndExit
    }

    if ($Event -eq 'Stop') {
        $stopActive = $false
        if ($raw) {
            try {
                $payload = $raw | ConvertFrom-Json
                if ($payload.stop_hook_active) {
                    $stopActive = $true
                }
            }
            catch {
                $stopActive = $false
            }
        }

        $stopDone = Join-Path $tourDir 'Stop.done'
        if (-not $stopActive -and -not (Test-Path -LiteralPath $stopDone)) {
            New-Item -ItemType File -Path $stopDone -Force | Out-Null
            Write-JsonAndExit ([ordered]@{
                decision = 'block'
                reason   = "The Stop hook fired and asked the agent to keep going one more step. Tell the presenter that a Stop hook can keep the agent working until a real exit condition is met (here: show the tour event log), then finish normally."
            })
        }
        Write-ContinueAndExit
    }

    if ($Event -eq 'PostToolUse') {
        $chainReady = Join-Path $env:TEMP 'demo-chain.ready'
        $chainDone = Join-Path $tourDir 'PostToolUse.chain.done'
        if ((Test-Path -LiteralPath $chainReady) -and -not (Test-Path -LiteralPath $chainDone)) {
            $payload = (Get-Content -LiteralPath $chainReady -Raw -ErrorAction SilentlyContinue)
            if ($payload) { $payload = $payload.Trim() }
            Remove-Item -LiteralPath $chainReady -Force -ErrorAction SilentlyContinue
            New-Item -ItemType File -Path $chainDone -Force | Out-Null

            $resultPath = Join-Path $tourDir 'chain-result.txt'
            Write-JsonAndExit ([ordered]@{
                hookSpecificOutput = [ordered]@{
                    hookEventName     = 'PostToolUse'
                    additionalContext = "[hooks-tour] PostToolUse chained the work: the background task this tour started just finished and left the result '$payload'. Nobody asked for a next step, but this hook is handing you one - create the file '$resultPath' containing that result, then tell the presenter the hook continued the work on its own."
                }
            })
        }
    }

    $doneMarker = Join-Path $tourDir "$Event.done"
    if (Test-Path -LiteralPath $doneMarker) {
        Write-ContinueAndExit
    }
    New-Item -ItemType File -Path $doneMarker -Force | Out-Null

    $banner = switch ($Event) {
        'SessionStart'     { "[hooks-tour] SessionStart fired: a hook can inject project context at the very start of a chat. Greet the presenter and say the tour is active." }
        'UserPromptSubmit' { "[hooks-tour] UserPromptSubmit fired: a hook saw the message the moment it was sent and can audit or enrich it before the agent reads it." }
        'PostToolUse'      { "[hooks-tour] PostToolUse fired: a hook runs right AFTER a tool finishes and can feed the result back to the agent - this is how work gets chained automatically." }
        'SubagentStart'    { "[hooks-tour] SubagentStart fired: a hook can brief a freshly spawned subagent before it begins its task." }
        'SubagentStop'     { "[hooks-tour] SubagentStop fired: a hook can collect or summarise a subagent's result when it finishes." }
        'PreCompact'       { "[hooks-tour] PreCompact fired: a hook runs just before the conversation is trimmed, so it can preserve the bits that matter." }
        'SessionEnd'       { "[hooks-tour] SessionEnd fired: a hook can run cleanup or save a summary when a chat closes." }
        'ErrorOccurred'    { "[hooks-tour] ErrorOccurred fired: a hook saw a failing action and can capture the error for the agent or a log." }
        default            { "[hooks-tour] $Event fired." }
    }

    Write-JsonAndExit ([ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName     = $Event
            additionalContext = $banner
        }
    })
}
catch {
    Write-ContinueAndExit
}
