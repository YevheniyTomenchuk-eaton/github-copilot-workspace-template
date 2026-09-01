<#
.SYNOPSIS
Deterministic commit + push for the `ship` flow. Optionally creates a fresh
feature branch at the current HEAD first (the safe way to move a dirty tree off
the base branch).

.DESCRIPTION
Encapsulates the only safe commit/push sequence, removing the inlined git snippets
from the ship prompt:

  - With -NewBranch: creates the branch at the current HEAD (carrying any
    uncommitted changes with it - the safe exception to the no-dirty-switch rule).
    Used when the current branch is the base branch (never commit on the base).
  - Stages everything and commits with -CommitMessage when the working tree is
    dirty. When the tree is already clean (e.g. right after rebase-onto-base.ps1
    cherry-picked the work), it skips the commit and only pushes.
  - Pushes with upstream tracking.

Non-destructive: no stash, clean, reset, or switch to an existing branch. Refuses
to run on the base branch unless -NewBranch moves the work onto a feature branch
first.

.PARAMETER CommitMessage
Message for the commit. Required when the working tree is dirty; ignored when the
tree is already clean (push-only).

.PARAMETER NewBranch
When set, create this branch at the current HEAD before committing. Must not
already exist. Required when the current branch is the base branch.

.PARAMETER Base
The base branch to guard against committing on directly. Defaults to main (it is
not always main - a repo may target develop, a release branch, etc.).

.OUTPUTS
RESULT=<pushed|stopped-not-a-git-repo|stopped-detached-head|stopped-on-base-without-newbranch|stopped-missing-commit-message|stopped-branch-exists|stopped-nothing-to-push>
BRANCH=<name|empty>
COMMITTED=<true|false>
COMMIT=<sha|empty>
PUSHED=<true|false>
SKIPPED_SUBMODULES=<comma-separated submodule paths whose gitlink change was excluded from the commit|empty>
STOP_REASON=<reason|empty>
#>
[CmdletBinding()]
param(
    [string]$CommitMessage,
    [string]$NewBranch,
    [ValidateNotNullOrEmpty()]
    [string]$Base = 'main'
)

$ErrorActionPreference = 'Stop'

$gitCommandScript = Join-Path (Split-Path -Parent $PSCommandPath) 'invoke-git-command.ps1'
. $gitCommandScript

function Format-CommandOutput {
    param([object[]]$OutputLines)

    $lines = @($OutputLines | ForEach-Object { [string]$_ })
    if ($lines.Count -eq 0) {
        return '<no output>'
    }

    return [string]::Join([Environment]::NewLine, $lines)
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

function Invoke-GitOrThrow {
    param(
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$FailureMessage
    )

    $result = Invoke-GitCommand -Arguments $Arguments
    if ($result.ExitCode -ne 0) {
        $outputText = Format-CommandOutput -OutputLines $result.Output
        throw "$FailureMessage (exit $($result.ExitCode)). Git output: $outputText"
    }

    return Get-TrimmedParseableText -Value $result.Output
}

function Get-CurrentBranch {
    $result = Invoke-GitCommand -Arguments @('branch', '--show-current')
    if ($result.ExitCode -ne 0) {
        return ''
    }

    return Get-TrimmedParseableText -Value $result.Output
}

function Get-StagedSubmodulePath {
    $result = Invoke-GitCommand -Arguments @('diff', '--cached', '--raw', '--no-renames', '--ignore-submodules=none')
    if ($result.ExitCode -ne 0) {
        return @()
    }

    $paths = New-Object System.Collections.Generic.List[string]
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
            $paths.Add($tabSplit[1].Trim())
        }
    }

    return $paths.ToArray()
}

function Write-Stop {
    param(
        [Parameter(Mandatory)][string]$Result,
        [Parameter(Mandatory)][string]$Reason,
        [string]$Branch = '',
        [string]$SkippedSubmodules = ''
    )

    "RESULT=$Result"
    "BRANCH=$Branch"
    "COMMITTED=false"
    "COMMIT="
    "PUSHED=false"
    "SKIPPED_SUBMODULES=$SkippedSubmodules"
    "STOP_REASON=$Reason"
}

if ((Invoke-GitCommand -Arguments @('rev-parse', '--git-dir')).ExitCode -ne 0) {
    Write-Stop -Result 'stopped-not-a-git-repo' -Reason 'not-a-git-repo'
    return
}

$branch = Get-CurrentBranch
if ([string]::IsNullOrWhiteSpace($branch)) {
    Write-Stop -Result 'stopped-detached-head' -Reason 'detached-head'
    return
}

if ($branch -eq $Base -and [string]::IsNullOrWhiteSpace($NewBranch)) {
    Write-Stop -Result 'stopped-on-base-without-newbranch' -Reason 'on-base-without-newbranch' -Branch $branch
    return
}

if (-not [string]::IsNullOrWhiteSpace($NewBranch)) {
    if ((Invoke-GitCommand -Arguments @('show-ref', '--verify', '--quiet', "refs/heads/$NewBranch")).ExitCode -eq 0) {
        Write-Stop -Result 'stopped-branch-exists' -Reason 'branch-exists' -Branch $branch
        return
    }

    Invoke-GitOrThrow -Arguments @('checkout', '-b', $NewBranch) -FailureMessage "Failed to create branch $NewBranch" | Out-Null
    $branch = Get-CurrentBranch
}

$dirty = Invoke-GitOrThrow -Arguments @('status', '--porcelain') -FailureMessage 'Failed to inspect working tree'
$isDirty = -not [string]::IsNullOrEmpty($dirty)

$committed = $false
$commit = ''
$skippedSubmodules = @()

if ($isDirty) {
    if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
        Write-Stop -Result 'stopped-missing-commit-message' -Reason 'missing-commit-message' -Branch $branch
        return
    }

    Invoke-GitOrThrow -Arguments @('add', '-A') -FailureMessage 'Failed to stage changes' | Out-Null

    $skippedSubmodules = @(Get-StagedSubmodulePath)
    foreach ($submodulePath in $skippedSubmodules) {
        Invoke-GitOrThrow -Arguments @('reset', '-q', '--', $submodulePath) -FailureMessage "Failed to unstage submodule $submodulePath" | Out-Null
    }

    $hasStagedChanges = (Invoke-GitCommand -Arguments @('diff', '--cached', '--quiet')).ExitCode -ne 0
    if ($hasStagedChanges) {
        Invoke-GitOrThrow -Arguments @('commit', '-m', $CommitMessage) -FailureMessage 'Failed to commit' | Out-Null
        $committed = $true
    }
}

$commit = Invoke-GitOrThrow -Arguments @('rev-parse', 'HEAD') -FailureMessage 'Failed to read HEAD'

$hasUpstream = (Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}')).ExitCode -eq 0

if (-not $committed -and $hasUpstream) {
    $ahead = Get-TrimmedParseableText -Value (Invoke-GitCommand -Arguments @('rev-list', '--count', '@{upstream}..HEAD')).Output
    if ($ahead -eq '0') {
        Write-Stop -Result 'stopped-nothing-to-push' -Reason 'nothing-to-push' -Branch $branch `
            -SkippedSubmodules ([string]::Join(',', $skippedSubmodules))
        return
    }
}

Invoke-GitOrThrow -Arguments @('push', '-u', 'origin', $branch) -FailureMessage "Failed to push $branch" | Out-Null

"RESULT=pushed"
"BRANCH=$branch"
"COMMITTED=$(if ($committed) { 'true' } else { 'false' })"
"COMMIT=$commit"
"PUSHED=true"
"SKIPPED_SUBMODULES=$([string]::Join(',', $skippedSubmodules))"
"STOP_REASON="
