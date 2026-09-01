<#
.SYNOPSIS
Deterministic preflight for the `ship` flow: inspect repo state and decide the
single correct ship path, so the agent never has to reason through the branch/PR
decision tree by hand.

.DESCRIPTION
Reads the working-tree state, current branch, and the current branch's PR state
(via gh), then emits one SITUATION and one ACTION. The `ship` prompt maps the
ACTION to exactly one follow-up script - no improvised git sequences.

Non-destructive: only reads state (status, branch, gh pr view). Makes no commits,
no branch changes, no pushes.

.OUTPUTS
RESULT=<ok|stopped-not-a-git-repo|stopped-detached-head>
SITUATION=<no-changes|on-base|feature-open-pr|feature-merged-pr|feature-other>
ACTION=<stop-no-changes|branch-commit-push-pr|commit-push|squash-recovery|commit-push-pr>
BRANCH=<name|empty>
DIRTY=<true|false>
HAS_CHANGES=<true|false>
PR_STATE=<OPEN|MERGED|CLOSED|NONE>
PR_NUMBER=<n|empty>
PR_URL=<url|empty>
SUBMODULE_CHANGES=<comma-separated submodule paths with a pending gitlink change; ship excludes these from the commit|empty>
STOP_REASON=<reason|empty>

ACTION -> follow-up:
  stop-no-changes        nothing to ship; inform the user and stop.
  branch-commit-push-pr  commit-and-push.ps1 -NewBranch ai/<desc> -CommitMessage "<m>", then create-pr.ps1.
  commit-push            commit-and-push.ps1 -CommitMessage "<m>"  (push to the existing OPEN PR; do NOT create a PR).
  squash-recovery        rebase-onto-base.ps1 -NewBranch ai/<desc> -CommitMessage "<m>", then commit-and-push.ps1 (push only) + create-pr.ps1.
  commit-push-pr         commit-and-push.ps1 -CommitMessage "<m>", then create-pr.ps1.

.PARAMETER Base
The base branch you ship into. Defaults to main (it is not always main - a repo may
target develop, a release branch, etc.). Used to detect "on the base branch".
#>
[CmdletBinding()]
param(
    [ValidateNotNullOrEmpty()]
    [string]$Base = 'main'
)

$ErrorActionPreference = 'Stop'

function Get-TrimmedParseableText {
    param([object]$Value)

    if ($null -eq $Value) {
        return ''
    }

    if ($Value -is [array]) {
        $parseableLines = @(
            $Value |
            Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } |
            ForEach-Object { [string]$_ }
        )

        if ($parseableLines.Count -eq 0) {
            return ''
        }

        return [string]::Join([Environment]::NewLine, $parseableLines).Trim()
    }

    if ($Value -is [System.Management.Automation.ErrorRecord]) {
        return ''
    }

    return ([string]$Value).Trim()
}

function Invoke-Native {
    param(
        [Parameter(Mandatory)][string]$Exe,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $Exe @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previous
    }

    return [pscustomobject]@{ Output = $output; ExitCode = $exitCode }
}

function Get-SubmoduleChangePath {
    $paths = New-Object System.Collections.Generic.List[string]
    foreach ($argumentSet in @(
        @('diff', '--cached', '--raw', '--no-renames', '--ignore-submodules=none'),
        @('diff', '--raw', '--no-renames', '--ignore-submodules=none')
    )) {
        $result = Invoke-Native -Exe 'git' -Arguments $argumentSet
        if ($result.ExitCode -ne 0) {
            continue
        }

        foreach ($line in @($result.Output | ForEach-Object { [string]$_ })) {
            if ([string]::IsNullOrWhiteSpace($line)) {
                continue
            }

            $tabSplit = $line -split "`t", 2
            if ($tabSplit.Count -lt 2) {
                continue
            }

            $fields = ($tabSplit[0].TrimStart(':')) -split '\s+'
            if ($fields.Count -lt 2) {
                continue
            }

            if ($fields[0] -eq '160000' -or $fields[1] -eq '160000') {
                $candidate = $tabSplit[1].Trim()
                if (-not $paths.Contains($candidate)) {
                    $paths.Add($candidate)
                }
            }
        }
    }

    return $paths.ToArray()
}

function Write-Result {
    param(
        [string]$Result = 'ok',
        [string]$Situation = '',
        [string]$Action = '',
        [string]$Branch = '',
        [bool]$Dirty = $false,
        [bool]$HasChanges = $false,
        [string]$PrState = 'NONE',
        [string]$PrNumber = '',
        [string]$PrUrl = '',
        [string]$SubmoduleChanges = '',
        [string]$StopReason = ''
    )

    "RESULT=$Result"
    "SITUATION=$Situation"
    "ACTION=$Action"
    "BRANCH=$Branch"
    "DIRTY=$(if ($Dirty) { 'true' } else { 'false' })"
    "HAS_CHANGES=$(if ($HasChanges) { 'true' } else { 'false' })"
    "PR_STATE=$PrState"
    "PR_NUMBER=$PrNumber"
    "PR_URL=$PrUrl"
    "SUBMODULE_CHANGES=$SubmoduleChanges"
    "STOP_REASON=$StopReason"
}

if ((Invoke-Native -Exe 'git' -Arguments @('rev-parse', '--git-dir')).ExitCode -ne 0) {
    Write-Result -Result 'stopped-not-a-git-repo' -StopReason 'not-a-git-repo'
    return
}

$branch = Get-TrimmedParseableText -Value (Invoke-Native -Exe 'git' -Arguments @('branch', '--show-current')).Output
if ([string]::IsNullOrWhiteSpace($branch)) {
    Write-Result -Result 'stopped-detached-head' -StopReason 'detached-head'
    return
}

$porcelain = Get-TrimmedParseableText -Value (Invoke-Native -Exe 'git' -Arguments @('status', '--porcelain')).Output
$hasChanges = -not [string]::IsNullOrEmpty($porcelain)

$submoduleChanges = [string]::Join(',', @(Get-SubmoduleChangePath))

if (-not $hasChanges) {
    Write-Result -Situation 'no-changes' -Action 'stop-no-changes' -Branch $branch `
        -Dirty $false -HasChanges $false -SubmoduleChanges $submoduleChanges -StopReason 'no-changes'
    return
}

if ($branch -eq $Base) {
    Write-Result -Situation 'on-base' -Action 'branch-commit-push-pr' -Branch $branch `
        -Dirty $true -HasChanges $true -PrState 'NONE' -SubmoduleChanges $submoduleChanges
    return
}

$prView = Invoke-Native -Exe 'gh' -Arguments @('pr', 'view', '--json', 'state,number,url')
$prState = 'NONE'
$prNumber = ''
$prUrl = ''

if ($prView.ExitCode -eq 0) {
    $jsonText = Get-TrimmedParseableText -Value $prView.Output
    if (-not [string]::IsNullOrEmpty($jsonText)) {
        try {
            $pr = $jsonText | ConvertFrom-Json
            if ($pr.state) {
                $prState = [string]$pr.state
            }
            if ($pr.number) {
                $prNumber = [string]$pr.number
            }
            if ($pr.url) {
                $prUrl = [string]$pr.url
            }
        }
        catch {
            $prState = 'NONE'
        }
    }
}

switch ($prState) {
    'OPEN' {
        Write-Result -Situation 'feature-open-pr' -Action 'commit-push' -Branch $branch `
            -Dirty $true -HasChanges $true -PrState $prState -PrNumber $prNumber -PrUrl $prUrl -SubmoduleChanges $submoduleChanges
    }
    'MERGED' {
        Write-Result -Situation 'feature-merged-pr' -Action 'squash-recovery' -Branch $branch `
            -Dirty $true -HasChanges $true -PrState $prState -PrNumber $prNumber -PrUrl $prUrl -SubmoduleChanges $submoduleChanges
    }
    default {
        Write-Result -Situation 'feature-other' -Action 'commit-push-pr' -Branch $branch `
            -Dirty $true -HasChanges $true -PrState $prState -PrNumber $prNumber -PrUrl $prUrl -SubmoduleChanges $submoduleChanges
    }
}
