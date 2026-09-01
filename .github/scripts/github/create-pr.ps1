<#
.SYNOPSIS
Deterministic, idempotent PR creation for the `ship` flow.

.DESCRIPTION
Creates a pull request from the current branch into the base branch using a body
read from a UTF-8 file. The agent authors the title and the body file (content is
judgment, not logic); this script owns the mechanical, error-prone part:

  - Skips creation when an OPEN PR already exists for the current branch
    (returns the existing URL) - never opens a duplicate.
  - Passes the body via --body-file so backticks / markdown / em-dashes are never
    corrupted by console encoding (the github skill section 3 rule).

Author the body file with your file-creation tool (UTF-8). Do NOT round-trip a PR
body through a captured shell variable.

.PARAMETER Title
PR title.

.PARAMETER BodyFile
Path to a UTF-8 file containing the PR body markdown.

.PARAMETER Base
Base branch. Defaults to main.

.PARAMETER ClonePath
Optional path to a checked-out clone (e.g. a disposable slot `sources\dev\dev-N`).
When supplied, every git/gh call runs against that clone so the PR is created for the
branch checked out there, and the caller's own working directory is left unchanged.
Used by the branch-grouping flow, which creates the grouped PR from a claimed slot.
When omitted, the script operates on the current directory (the `ship` flow).

.OUTPUTS
RESULT=<created|already-exists|stopped-not-a-git-repo|stopped-detached-head|stopped-on-base|stopped-body-file-missing>
BRANCH=<name|empty>
PR_NUMBER=<n|empty>
PR_URL=<url|empty>
CREATED=<true|false>
STOP_REASON=<reason|empty>
#>
[CmdletBinding()]
param(
    [string]$Title = $(throw 'Required parameter -Title was not provided.'),
    [string]$BodyFile = $(throw 'Required parameter -BodyFile was not provided.'),
    [string]$Base = 'main',
    [string]$ClonePath = ''
)

$ErrorActionPreference = 'Stop'

if ($ClonePath) {
    if (-not (Test-Path -LiteralPath $ClonePath -PathType Container)) {
        throw "Clone path not found: $ClonePath"
    }
    if (Test-Path -LiteralPath $BodyFile -PathType Leaf) {
        $BodyFile = (Resolve-Path -LiteralPath $BodyFile).Path
    }
}

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

function Get-CurrentBranch {
    $result = Invoke-Native -Exe 'git' -Arguments @('branch', '--show-current')
    if ($result.ExitCode -ne 0) {
        return ''
    }

    return Get-TrimmedParseableText -Value $result.Output
}

function Write-Stop {
    param(
        [Parameter(Mandatory)][string]$Result,
        [Parameter(Mandatory)][string]$Reason,
        [string]$Branch = ''
    )

    "RESULT=$Result"
    "BRANCH=$Branch"
    "PR_NUMBER="
    "PR_URL="
    "CREATED=false"
    "STOP_REASON=$Reason"
}

function Read-PrView {
    $view = Invoke-Native -Exe 'gh' -Arguments @('pr', 'view', '--json', 'state,number,url')
    if ($view.ExitCode -ne 0) {
        return $null
    }

    $jsonText = Get-TrimmedParseableText -Value $view.Output
    if ([string]::IsNullOrEmpty($jsonText)) {
        return $null
    }

    try {
        return $jsonText | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

if ($ClonePath) {
    Push-Location -LiteralPath $ClonePath
}
try {
    if ((Invoke-Native -Exe 'git' -Arguments @('rev-parse', '--git-dir')).ExitCode -ne 0) {
        Write-Stop -Result 'stopped-not-a-git-repo' -Reason 'not-a-git-repo'
        return
    }

    $branch = Get-CurrentBranch
    if ([string]::IsNullOrWhiteSpace($branch)) {
        Write-Stop -Result 'stopped-detached-head' -Reason 'detached-head'
        return
    }

    if ($branch -eq $Base) {
        Write-Stop -Result 'stopped-on-base' -Reason 'on-base' -Branch $branch
        return
    }

    if (-not (Test-Path -LiteralPath $BodyFile -PathType Leaf)) {
        Write-Stop -Result 'stopped-body-file-missing' -Reason 'body-file-missing' -Branch $branch
        return
    }

    $existing = Read-PrView
    if ($null -ne $existing -and $existing.state -eq 'OPEN') {
        "RESULT=already-exists"
        "BRANCH=$branch"
        "PR_NUMBER=$([string]$existing.number)"
        "PR_URL=$([string]$existing.url)"
        "CREATED=false"
        "STOP_REASON="
        return
    }

    $create = Invoke-Native -Exe 'gh' -Arguments @(
        'pr', 'create', '--base', $Base, '--head', $branch, '--title', $Title, '--body-file', $BodyFile
    )
    if ($create.ExitCode -ne 0) {
        $outputText = Get-TrimmedParseableText -Value $create.Output
        throw "Failed to create PR (exit $($create.ExitCode)). gh output: $outputText"
    }

    $pr = Read-PrView
    $prNumber = ''
    $prUrl = Get-TrimmedParseableText -Value $create.Output
    if ($null -ne $pr) {
        if ($pr.number) {
            $prNumber = [string]$pr.number
        }
        if ($pr.url) {
            $prUrl = [string]$pr.url
        }
    }

    "RESULT=created"
    "BRANCH=$branch"
    "PR_NUMBER=$prNumber"
    "PR_URL=$prUrl"
    "CREATED=true"
    "STOP_REASON="
}
finally {
    if ($ClonePath) {
        Pop-Location
    }
}
