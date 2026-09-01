<#
.SYNOPSIS
  Runs Git while preserving its output and exit code under Windows PowerShell 5.1.

.DESCRIPTION
  Dot-source this library from scripts that need to inspect combined Git stdout and stderr.
  Windows PowerShell 5.1 represents redirected native stderr as ErrorRecord objects and can
  terminate a script when ErrorActionPreference is Stop, even when Git exits successfully.
  Invoke-GitCommand temporarily uses Continue, captures LASTEXITCODE immediately, and returns
  normalized text lines without hiding genuine nonzero exits.
#>

function Invoke-GitCommand {
    [CmdletBinding()]
    param(
        [string[]]$Arguments = $(throw 'Required parameter -Arguments was not provided.')
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'

    try {
        $gitCommand = (Get-Command git -CommandType Application -ErrorAction Stop).Source
        $rawOutput = & $gitCommand @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    $output = @(
        $rawOutput |
            ForEach-Object {
                if ($_ -is [System.Management.Automation.ErrorRecord]) {
                    $_.Exception.Message
                }
                else {
                    [string]$_
                }
            }
    )

    [pscustomobject]@{
        Output = $output
        ExitCode = $exitCode
    }
}
