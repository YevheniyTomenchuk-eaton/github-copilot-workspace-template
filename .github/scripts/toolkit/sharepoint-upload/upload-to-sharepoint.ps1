param(
    [string[]]$LocalPath = $(throw 'Required parameter -LocalPath was not provided.'),
    [string]$SiteUrl = $(throw 'Required parameter -SiteUrl was not provided.'),
    [string]$TargetFolder = $(throw 'Required parameter -TargetFolder was not provided.'),
    [switch]$Overwrite,
    [switch]$CreateFolder
)

$ErrorActionPreference = 'Stop'

$siteUri = [System.Uri]::new($SiteUrl)
$SitePath = $siteUri.AbsolutePath.TrimEnd('/')
if ([string]::IsNullOrWhiteSpace($SitePath)) {
    throw "SiteUrl '$SiteUrl' has no site path. Use the full site URL, e.g. https://contoso.sharepoint.com/sites/MySite"
}

if (-not $TargetFolder.StartsWith($SitePath + '/', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "TargetFolder '$TargetFolder' must start with the site path '$SitePath/'"
}

$resolved = New-Object 'System.Collections.Generic.List[object]'
foreach ($p in $LocalPath) {
    $items = Get-Item -LiteralPath $p -ErrorAction Stop
    foreach ($it in $items) {
        if ($it.PSIsContainer) {
            Get-ChildItem -LiteralPath $it.FullName -File -Recurse | ForEach-Object {
                $rel = $_.FullName.Substring($it.FullName.Length).TrimStart('\','/') -replace '\\','/'
                $resolved.Add([pscustomobject]@{ Local = $_.FullName; RelPath = $rel; Size = $_.Length })
            }
        } else {
            $resolved.Add([pscustomobject]@{ Local = $it.FullName; RelPath = $it.Name; Size = $it.Length })
        }
    }
}
if ($resolved.Count -eq 0) { throw "No files found for upload." }

$targetUrl = ("$($siteUri.GetLeftPart([System.UriPartial]::Authority))$TargetFolder") -replace ' ', '%20'

Write-Host "Will upload $($resolved.Count) file(s), total $([math]::Round((($resolved | Measure-Object Size -Sum).Sum)/1MB,2)) MB"
Write-Host "Target: $targetUrl"
Write-Host ("Overwrite policy: " + $(if ($Overwrite) { 'REPLACE existing files (same-size and different-size)' } else { 'SKIP same-size, FAIL on size mismatch' }))

if (-not (Get-Module -ListAvailable -Name SharePointPnPPowerShellOnline)) {
    Write-Host "SharePointPnPPowerShellOnline is missing; installing for current user..."
    Install-Module -Name SharePointPnPPowerShellOnline -Scope CurrentUser -Force -AllowClobber
}

Import-Module SharePointPnPPowerShellOnline -WarningAction Ignore
Write-Host "`nConnecting (browser sign-in)..."
Connect-PnPOnline -Url $SiteUrl -UseWebLogin

$ctx = Get-PnPContext
$web = $ctx.Web
$ctx.Load($web)
$ctx.ExecuteQuery()

function Ensure-Folder {
    param([string]$ServerRel)
    try {
        $f = $web.GetFolderByServerRelativeUrl($ServerRel)
        $ctx.Load($f)
        $ctx.ExecuteQuery()
        return
    } catch { }
    $parts = $ServerRel.Substring($SitePath.Length).TrimStart('/') -split '/'
    $cur = $SitePath
    foreach ($p in $parts) {
        $next = "$cur/$p"
        try {
            $f = $web.GetFolderByServerRelativeUrl($next)
            $ctx.Load($f)
            $ctx.ExecuteQuery()
        } catch {
            $parent = $web.GetFolderByServerRelativeUrl($cur)
            $parent.Folders.Add($p) | Out-Null
            $ctx.ExecuteQuery()
            Write-Host "  created folder $next"
        }
        $cur = $next
    }
}

if ($CreateFolder) { Ensure-Folder -ServerRel $TargetFolder }
else {
    try {
        $check = $web.GetFolderByServerRelativeUrl($TargetFolder)
        $ctx.Load($check)
        $ctx.ExecuteQuery()
    } catch {
        throw "Target folder does not exist: $TargetFolder (pass -CreateFolder to auto-create)"
    }
}

function Upload-One {
    param([string]$LocalFile, [string]$RelPath, [long]$Size, [string]$BaseFolder)

    $segments = $RelPath -split '/'
    $fileName = $segments[-1]
    $subFolder = if ($segments.Count -gt 1) {
        "$BaseFolder/" + ($segments[0..($segments.Count-2)] -join '/')
    } else { $BaseFolder }

    if ($subFolder -ne $BaseFolder) { Ensure-Folder -ServerRel $subFolder }

    $fileRel = "$subFolder/$fileName"

    try {
        $existing = $web.GetFileByServerRelativeUrl($fileRel)
        $ctx.Load($existing)
        $ctx.ExecuteQuery()
        if ($existing.Length -eq $Size -and -not $Overwrite) {
            Write-Host ("`nSKIP {0} (already present, {1:N0} bytes)" -f $RelPath, $Size)
            return
        }
        if (-not $Overwrite) {
            throw "File exists with different size ($($existing.Length) vs $Size): $fileRel. Re-run with -Overwrite to replace."
        }
        Write-Host ("`nREPLACE {0} (server={1} bytes, local={2} bytes)..." -f $RelPath, $existing.Length, $Size)
        $existing.DeleteObject()
        $ctx.ExecuteQuery()
    } catch [Microsoft.SharePoint.Client.ServerException] {
        if ($_.Exception.ServerErrorTypeName -notlike '*FileNotFoundException*' -and $_.Exception.Message -notlike '*does not exist*') { throw }
    } catch {
        if ($_.Exception.Message -notlike '*does not exist*' -and $_.Exception.Message -notlike '*File Not Found*') { throw }
    }

    $chunkSize = 8MB
    $totalChunks = [int][Math]::Ceiling($Size / $chunkSize)
    if ($totalChunks -eq 0) { $totalChunks = 1 }
    Write-Host ("`nUPLOAD {0} ({1:N2} MB, {2} chunk(s))..." -f $RelPath, ($Size/1MB), $totalChunks)

    $folder = $web.GetFolderByServerRelativeUrl($subFolder)
    $ctx.Load($folder)
    $ctx.ExecuteQuery()

    if ($Size -le $chunkSize) {
        $fs = [IO.File]::OpenRead($LocalFile)
        try {
            $fci = New-Object Microsoft.SharePoint.Client.FileCreationInformation
            $fci.Url = $fileName
            $fci.Overwrite = $true
            $fci.ContentStream = $fs
            $newFile = $folder.Files.Add($fci)
            $ctx.Load($newFile)
            $ctx.ExecuteQuery()
        } finally { $fs.Dispose() }
        Write-Host "  done (single PUT)"
        return
    }

    $emptyCi = New-Object Microsoft.SharePoint.Client.FileCreationInformation
    $emptyCi.Url = $fileName
    $emptyCi.Overwrite = $true
    $emptyStream = New-Object System.IO.MemoryStream
    $emptyCi.ContentStream = $emptyStream
    try {
        $file = $folder.Files.Add($emptyCi)
        $ctx.Load($file)
        $ctx.ExecuteQuery()
    } finally {
        $emptyStream.Dispose()
    }

    $uploadId = [Guid]::NewGuid()
    $fs = [IO.File]::OpenRead($LocalFile)
    try {
        $buffer = New-Object byte[] $chunkSize
        $offset = 0L
        for ($i = 0; $i -lt $totalChunks; $i++) {
            $read = $fs.Read($buffer, 0, $chunkSize)
            $ms = New-Object System.IO.MemoryStream
            $ms.Write($buffer, 0, $read)
            $ms.Position = 0

            $isLast  = ($i -eq $totalChunks - 1)
            $isFirst = ($i -eq 0)

            $attempt = 0
            while ($true) {
                try {
                    if ($isFirst) {
                        $file.StartUpload($uploadId, $ms) | Out-Null
                    } elseif ($isLast) {
                        $file.FinishUpload($uploadId, $offset, $ms) | Out-Null
                    } else {
                        $file.ContinueUpload($uploadId, $offset, $ms) | Out-Null
                    }
                    $ctx.ExecuteQuery()
                    break
                } catch {
                    $attempt++
                    if ($attempt -ge 4) { throw }
                    $sleep = [Math]::Min(60, 5 * $attempt)
                    Write-Host ("    retry {0}/4 chunk {1}/{2} after {3}s: {4}" -f $attempt, ($i+1), $totalChunks, $sleep, $_.Exception.Message)
                    Start-Sleep -Seconds $sleep
                    $ms.Position = 0
                }
            }

            $ms.Dispose()
            $offset += $read
            $pct = [math]::Round(($offset / $Size) * 100, 1)
            Write-Host ("  chunk {0,4}/{1} | {2,7:N2} MB / {3,7:N2} MB | {4,5:N1}%" -f ($i+1), $totalChunks, ($offset/1MB), ($Size/1MB), $pct)
        }
    } finally {
        $fs.Dispose()
    }

    $check = $web.GetFileByServerRelativeUrl($fileRel)
    $ctx.Load($check)
    $ctx.ExecuteQuery()
    if ($check.Length -ne $Size) {
        throw "Size mismatch after upload: server=$($check.Length) expected=$Size for $fileRel"
    }
    Write-Host ("  verified: {0:N0} bytes" -f $check.Length)
}

foreach ($r in $resolved) {
    Upload-One -LocalFile $r.Local -RelPath $r.RelPath -Size $r.Size -BaseFolder $TargetFolder
}

Write-Host "`nAll uploads complete: $targetUrl"
Write-Host "OUTPUT=$targetUrl"
Write-Host "FILES=$($resolved.Count)"
Disconnect-PnPOnline
