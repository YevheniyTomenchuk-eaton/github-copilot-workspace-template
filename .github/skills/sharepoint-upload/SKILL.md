---
name: sharepoint-upload
description: "Upload local files or folders to any Microsoft 365 SharePoint folder, with safe overwrite semantics and CSOM chunked upload for large files (multi-GB). Generic — the site URL and target folder are supplied at call time, never hardcoded. Use whenever the user asks to publish, push, or upload a file to SharePoint (for example, sending a generated deck, workbook, or document to a team site)."
---

# SharePoint Upload

One uploader script puts any local file or folder onto a SharePoint folder you choose. **Read this whole file before using it** — the overwrite policy and folder-creation policy matter.

## Nothing is hardcoded

This skill never stores a tenant, site, or folder. The caller supplies them every run:

- **`-SiteUrl`** — the full SharePoint site URL, e.g. `https://contoso.sharepoint.com/sites/MyTeam`. The script derives the server-relative site path from it.
- **`-TargetFolder`** — the server-relative folder under that site, e.g. `/sites/MyTeam/Shared Documents/General/Reports`.

If either is missing, **ask the user** — never guess a URL.

## Uploader — `upload-to-sharepoint.ps1`

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\.github\scripts\toolkit\sharepoint-upload\upload-to-sharepoint.ps1 `
    -LocalPath 'C:\path\to\file-or-folder', 'C:\another\file.pdf' `
    -SiteUrl 'https://contoso.sharepoint.com/sites/MyTeam' `
    -TargetFolder '/sites/MyTeam/Shared Documents/General/Reports' `
    -CreateFolder
```

### Parameters

| Name | Required | Notes |
|---|---|---|
| `-LocalPath` | yes | One or more files or folders. Folders are recursed; relative paths inside a folder are kept on SharePoint. |
| `-SiteUrl` | yes | Full site URL. The server-relative site path is derived from it. |
| `-TargetFolder` | yes | Server-relative SharePoint URL. Must start with the site path derived from `-SiteUrl`. |
| `-CreateFolder` | no | Create the target folder (and any missing parents under the site) if it does not exist. Without this switch, a missing folder is an error. |
| `-Overwrite` | no | **Default: SKIP same-size files, FAIL on size mismatch.** With this switch: existing files are replaced (same-size and different-size) to force an exact refresh. |

### Overwrite safety

The default is conservative on purpose. If a file at the target already exists with a **different** size, the script stops and asks you to re-run with `-Overwrite`. This stops an accidental clobber of the wrong file. Pass `-Overwrite` only when the caller really wants to replace, and tell the user clearly when you use it.

### Outputs

The script prints two machine-readable lines at the end:

```
OUTPUT=<final SharePoint folder URL>
FILES=<number of files uploaded>
```

Read these to report the result.

## Asking for inputs

- **Site URL and target folder** — ask the user if not provided. Never invent a URL.
- **Sign-in** — the script opens a browser window (`Connect-PnPOnline -UseWebLogin`). The user signs in once; the token is cached for the session. Never ask for a SharePoint password through `vscode_askQuestions`.

## How it works

- Resolves every local file (recursing folders, preserving relative paths).
- Connects with the legacy `SharePointPnPPowerShellOnline` module via browser sign-in. Installs it for the current user if missing.
- Uploads each file with CSOM. Files larger than 8 MB use chunked `StartUpload` / `ContinueUpload` / `FinishUpload`, retrying a chunk up to 4 times.
- Verifies the uploaded size matches the local size before moving on.

### Why CSOM, not REST

`Invoke-PnPSPRestMethod -Content $bytes` does not transmit `byte[]` as raw binary — it serializes them, breaking server-side offset checks at `FinishUpload` for files over ~250 MB. The script uses CSOM `Microsoft.SharePoint.Client.File.{StartUpload,ContinueUpload,FinishUpload}`, which sends real binary.

### Pitfalls

- **`AddUsingPath` without a body** writes a 4-byte JSON `null` and corrupts chunked sessions. The script creates the placeholder via `Files.Add(FileCreationInformation)` with an empty `MemoryStream`.
- **Legacy module warning banner** on every connect — ignore it. The new `PnP.PowerShell` module needs Entra ClientId setup this skill does not assume.
- **Long uploads** — start the command in async mode with a short initial timeout and wait for the completion notification.

## When NOT to use this

- Downloads, list edits, or permission changes — out of scope.
- Anywhere a site URL or folder is unknown — ask first; do not guess.
