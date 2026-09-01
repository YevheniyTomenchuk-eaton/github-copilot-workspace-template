<#
.SYNOPSIS
Deterministic squash-merge recovery: move new work off a stale (already-merged)
feature branch onto a fresh branch cut from latest origin/<base> (default main).

.DESCRIPTION
Many repos squash-merge PRs, so a merged feature branch's individual commits are NOT
in the base branch's history (the base has one squashed commit instead). Committing on
top of such a branch, or branching off it, makes every file from the merged PR
re-appear as "new" in the next PR. The safe, deterministic recovery is always the same:

  1. Capture the new work as ONE commit on the stale branch (its patch == exactly the
      new changes, because its parent already contains the merged files). This single
      commit is immune to the squash re-introduction problem.
  2. Fetch origin/<Base> and create a fresh branch based on origin/<Base>.
  3. Cherry-pick the captured commit(s) onto the fresh branch.
  4. Verify only the intended files differ from origin/<Base>.

The base branch is configurable via -Base (it is not always main - a repo may target
develop, a release branch, etc.).

This script performs steps 1-4 with no destructive operation (no stash, clean, reset,
or dirty-branch switch). It does NOT push or open a PR - the caller continues with the
push + PR steps of the ship flow.

Default (dirty working tree): stages all changes and commits them as a SINGLE commit
using -CommitMessage, then cherry-picks exactly that commit. This is the common case and
is fully automatic. Submodule gitlink drift is excluded from the capture commit.

Already-committed work (clean tree): pass the commit hash(es) to move via -CherryPick.
Committed-after-merge commits cannot be auto-detected (squash hides the link), so they
must be named explicitly.

.PARAMETER NewBranch
Name of the fresh branch to create from origin/<Base> (e.g. ai/<short-description>).
Must not already exist.

.PARAMETER Base
The base branch to cut the fresh branch from and diff against. Defaults to main.

.PARAMETER CommitMessage
Commit message used to capture a dirty working tree as a single commit. Required when
the working tree is dirty; ignored when the tree is clean and -CherryPick is supplied.

.PARAMETER CherryPick
Explicit commit hash(es) to move when the working tree is clean (work already committed).
When omitted and the tree is dirty, the script captures the tree as one commit and
cherry-picks that.

.OUTPUTS
RESULT=<rebased|conflicts|stopped-not-a-git-repo|stopped-detached-head|stopped-on-base|stopped-missing-commit-message|stopped-nothing-to-move|stopped-branch-exists>
START_BRANCH=<name|empty>
NEW_BRANCH=<name|empty>
CURRENT_BRANCH=<name|empty>
WORK_COMMIT=<sha|empty>          (the auto-capture commit; empty when -CherryPick was used)
CHERRY_PICKED=<sha,sha,...|empty> (commits successfully cherry-picked)
CHERRY_REMAINING=<sha,sha,...|empty> (commits not yet picked when a conflict halts the run)
CONFLICT_FILES=<path;path;...|empty> (unmerged paths when RESULT=conflicts)
DIFF_FILE_COUNT=<n|empty>        (files differing from origin/<Base> on success)
SKIPPED_SUBMODULES=<comma-separated submodule paths whose gitlink change was excluded from the capture commit|empty>
STOP_REASON=<reason|empty>
#>
[CmdletBinding()]
param(
    [string]$NewBranch = $(throw 'Required parameter -NewBranch was not provided.'),

    [ValidateNotNullOrEmpty()]
    [string]$Base = 'main',

    [string]$CommitMessage,

    [string[]]$CherryPick
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

function Test-TransientFetchRefUpdateFailure {
    param(
        [Parameter(Mandatory)]
        [string]$GitOutputText,

        [Parameter(Mandatory)]
        [string]$BaseBranch
    )

    $remoteRefPattern = [regex]::Escape("refs/remotes/origin/$BaseBranch")

    return (
        $GitOutputText -match "cannot lock ref '$remoteRefPattern'" -and
        $GitOutputText -match 'is at [0-9a-f]{40} but expected [0-9a-f]{40}' -and
        $GitOutputText -match 'unable to update local ref'
    )
}

function Invoke-OriginFetch {
    param(
        [Parameter(Mandatory)]
        [string]$BaseBranch
    )

    $maxAttempts = 2

    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        $fetchResult = Invoke-GitCommand -Arguments @('fetch', 'origin', $BaseBranch)
        if ($fetchResult.ExitCode -eq 0) {
            return $fetchResult
        }

        $fetchOutputText = Format-CommandOutput -OutputLines $fetchResult.Output
        $canRetry =
            $attempt -lt $maxAttempts -and
            (Test-TransientFetchRefUpdateFailure -GitOutputText $fetchOutputText -BaseBranch $BaseBranch)

        if (-not $canRetry) {
            throw "Failed to fetch origin/$BaseBranch (exit $($fetchResult.ExitCode)). Git output: $fetchOutputText"
        }
    }
}

function Invoke-GitOrThrow {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments,
        [Parameter(Mandatory)]
        [string]$FailureMessage
    )

    $result = Invoke-GitCommand -Arguments $Arguments
    if ($result.ExitCode -ne 0) {
        $outputText = Format-CommandOutput -OutputLines $result.Output
        throw "$FailureMessage (exit $($result.ExitCode)). Git output: $outputText"
    }

    return Get-TrimmedParseableText -Value $result.Output
}

function Get-CurrentBranch {
    $branchResult = Invoke-GitCommand -Arguments @('branch', '--show-current')
    if ($branchResult.ExitCode -ne 0) {
        return ''
    }

    return Get-TrimmedParseableText -Value $branchResult.Output
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
        [string]$StartBranch = '',
        [string]$WorkCommit = '',
        [string]$SkippedSubmodules = ''
    )

    "RESULT=$Result"
    "START_BRANCH=$StartBranch"
    "NEW_BRANCH="
    "CURRENT_BRANCH=$(Get-CurrentBranch)"
    "WORK_COMMIT=$WorkCommit"
    "CHERRY_PICKED="
    "CHERRY_REMAINING="
    "CONFLICT_FILES="
    "DIFF_FILE_COUNT="
    "SKIPPED_SUBMODULES=$SkippedSubmodules"
    "STOP_REASON=$Reason"
}

if ((Invoke-GitCommand -Arguments @('rev-parse', '--git-dir')).ExitCode -ne 0) {
    Write-Stop -Result 'stopped-not-a-git-repo' -Reason 'not-a-git-repo'
    return
}

$startBranch = Get-CurrentBranch
if ([string]::IsNullOrWhiteSpace($startBranch)) {
    Write-Stop -Result 'stopped-detached-head' -Reason 'detached-head'
    return
}

if ($startBranch -eq $Base) {
    Write-Stop -Result 'stopped-on-base' -Reason 'on-base' -StartBranch $startBranch
    return
}

if ((Invoke-GitCommand -Arguments @('show-ref', '--verify', '--quiet', "refs/heads/$NewBranch")).ExitCode -eq 0) {
    Write-Stop -Result 'stopped-branch-exists' -Reason 'branch-exists' -StartBranch $startBranch
    return
}

$dirty = Invoke-GitOrThrow -Arguments @('status', '--porcelain') -FailureMessage 'Failed to inspect working tree'
$isDirty = -not [string]::IsNullOrEmpty($dirty)

$workCommit = ''
$cherryList = @()
$skippedSubmodules = @()

if ($isDirty) {
    if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
        Write-Stop -Result 'stopped-missing-commit-message' -Reason 'missing-commit-message' -StartBranch $startBranch
        return
    }

    Invoke-GitOrThrow -Arguments @('add', '-A') -FailureMessage 'Failed to stage changes' | Out-Null

    $skippedSubmodules = @(Get-StagedSubmodulePath)
    foreach ($submodulePath in $skippedSubmodules) {
        Invoke-GitOrThrow -Arguments @('reset', '-q', '--', $submodulePath) -FailureMessage "Failed to unstage submodule $submodulePath" | Out-Null
    }

    $hasStagedChanges = (Invoke-GitCommand -Arguments @('diff', '--cached', '--quiet')).ExitCode -ne 0
    if (-not $hasStagedChanges) {
        Write-Stop -Result 'stopped-nothing-to-move' -Reason 'nothing-to-move-after-submodule-exclusion' -StartBranch $startBranch `
            -SkippedSubmodules ([string]::Join(',', $skippedSubmodules))
        return
    }

    Invoke-GitOrThrow -Arguments @('commit', '-m', $CommitMessage) -FailureMessage 'Failed to commit working tree' | Out-Null
    $workCommit = Invoke-GitOrThrow -Arguments @('rev-parse', 'HEAD') -FailureMessage 'Failed to read HEAD after commit'
    $cherryList = @($workCommit)
}
else {
    if (-not $CherryPick -or $CherryPick.Count -eq 0) {
        Write-Stop -Result 'stopped-nothing-to-move' -Reason 'nothing-to-move' -StartBranch $startBranch
        return
    }

    foreach ($ref in $CherryPick) {
        $resolved = Invoke-GitCommand -Arguments @('rev-parse', '--verify', "$ref^{commit}")
        if ($resolved.ExitCode -ne 0) {
            throw "Cherry-pick hash '$ref' could not be resolved to a commit."
        }
        $cherryList += (Get-TrimmedParseableText -Value $resolved.Output)
    }
}

Invoke-OriginFetch -BaseBranch $Base | Out-Null
Invoke-GitOrThrow -Arguments @('checkout', '-b', $NewBranch, "origin/$Base") -FailureMessage "Failed to create $NewBranch from origin/$Base" | Out-Null

$picked = @()
for ($i = 0; $i -lt $cherryList.Count; $i++) {
    $hash = $cherryList[$i]
    $pick = Invoke-GitCommand -Arguments @('cherry-pick', $hash)
    if ($pick.ExitCode -ne 0) {
        $conflictFiles = Get-TrimmedParseableText -Value (Invoke-GitCommand -Arguments @('diff', '--name-only', '--diff-filter=U')).Output
        $remaining = @($cherryList[$i..($cherryList.Count - 1)])

        "RESULT=conflicts"
        "START_BRANCH=$startBranch"
        "NEW_BRANCH=$NewBranch"
        "CURRENT_BRANCH=$(Get-CurrentBranch)"
        "WORK_COMMIT=$workCommit"
        "CHERRY_PICKED=$($picked -join ',')"
        "CHERRY_REMAINING=$($remaining -join ',')"
        "CONFLICT_FILES=$($conflictFiles -replace '\r?\n', ';')"
        "DIFF_FILE_COUNT="
        "SKIPPED_SUBMODULES=$([string]::Join(',', $skippedSubmodules))"
        "STOP_REASON=cherry-pick-conflict"
        return
    }

    $picked += $hash
}

$diffNames = Get-TrimmedParseableText -Value (Invoke-GitCommand -Arguments @('diff', '--name-only', "origin/$Base...HEAD")).Output
$diffCount = 0
if (-not [string]::IsNullOrEmpty($diffNames)) {
    $diffCount = @($diffNames -split '\r?\n').Count
}

"RESULT=rebased"
"START_BRANCH=$startBranch"
"NEW_BRANCH=$NewBranch"
"CURRENT_BRANCH=$(Get-CurrentBranch)"
"WORK_COMMIT=$workCommit"
"CHERRY_PICKED=$($picked -join ',')"
"CHERRY_REMAINING="
"CONFLICT_FILES="
"DIFF_FILE_COUNT=$diffCount"
"SKIPPED_SUBMODULES=$([string]::Join(',', $skippedSubmodules))"
"STOP_REASON="
