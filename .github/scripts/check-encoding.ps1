#Requires -Version 5.1
<#
.SYNOPSIS
    Local equivalent of the CI "encoding" check: UTF-8 without BOM + CRLF line
    endings for Markdown files.

.DESCRIPTION
    The CI workflow's encoding check verifies that every changed `.md` file is
    UTF-8 without a BOM and uses CRLF line endings. This script reproduces that
    check locally.

    By default it inspects the changed Markdown files reported by
    `git diff --name-only --diff-filter=ACMR HEAD -- '*.md'`. Pass -Path to
    check explicit files or directories instead (directories are scanned
    recursively for `.md` files).

.PARAMETER Path
    Optional explicit files or directories to check. When omitted, the changed
    Markdown files since HEAD are used.

.OUTPUTS
    KEY=value lines:
      FAIL=<file> (<reason>)   one per offending file
      CHECKED=<count>          number of files inspected
      FAILED=<count>           number of files that failed
      RESULT=pass|fail
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string[]]$Path
)

$ErrorActionPreference = 'Stop'

function Get-TargetFiles {
    param([string[]]$Inputs)

    if (-not $Inputs -or $Inputs.Count -eq 0) {
        $changed = git diff --name-only --diff-filter=ACMR HEAD -- '*.md'
        return @($changed | Where-Object { $_ -and (Test-Path -LiteralPath $_) })
    }

    $files = New-Object System.Collections.Generic.List[string]
    foreach ($entry in $Inputs) {
        if (-not (Test-Path -LiteralPath $entry)) { continue }
        $item = Get-Item -LiteralPath $entry
        if ($item.PSIsContainer) {
            Get-ChildItem -LiteralPath $entry -Recurse -Filter '*.md' -File |
                ForEach-Object { $files.Add($_.FullName) }
        }
        elseif ($item.Extension -ieq '.md') {
            $files.Add($item.FullName)
        }
    }
    return @($files)
}

$targets = Get-TargetFiles -Inputs $Path
$failed = 0

foreach ($file in $targets) {
    $bytes = [System.IO.File]::ReadAllBytes($file)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Output "FAIL=$file (UTF-8 BOM)"
        $failed++
        continue
    }
    $content = [System.IO.File]::ReadAllText($file)
    if ($content -match "(?<!`r)`n") {
        Write-Output "FAIL=$file (bare LF line endings, needs CRLF)"
        $failed++
    }
}

Write-Output "CHECKED=$($targets.Count)"
Write-Output "FAILED=$failed"
Write-Output ("RESULT=" + $(if ($failed -eq 0) { 'pass' } else { 'fail' }))

if ($failed -gt 0) { exit 1 }
