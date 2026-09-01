---
name: toolkit-excel-upload
description: "Upload a generated Excel .xlsx to a SharePoint folder you choose. Use when the user says 'upload the workbook to SharePoint', 'push the xlsx', or '/toolkit-excel-upload'."
---

# Upload Workbook to SharePoint

Push a built Excel workbook to a SharePoint folder. The site URL and folder are supplied by the user — nothing is hardcoded.

## 1. Load the rules

Read these before running anything:

1. [`sharepoint-upload`](../sharepoint-upload/SKILL.md) skill — the uploader, its parameters, and the overwrite policy.
2. [`toolkit.instructions.md`](../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Pick the file

Find the `.xlsx` to upload — usually the newest one under `toolkit/excel/YY-MM-DD-HHMM-short-description/workbook.xlsx`. If more than one exists, ask which one. Build it first with `/toolkit-excel-create` if none exists yet.

## 3. Ask for the destination

Ask the user for both, and never guess a URL:

- **Site URL** — e.g. `https://contoso.sharepoint.com/sites/MyTeam`.
- **Target folder** — server-relative, e.g. `/sites/MyTeam/Shared Documents/General/Reports`.

## 4. Upload

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .github/scripts/toolkit/sharepoint-upload/upload-to-sharepoint.ps1 -LocalPath "toolkit/excel/YY-MM-DD-HHMM-short-description/workbook.xlsx" -SiteUrl "<site-url>" -TargetFolder "<target-folder>" -CreateFolder
```

A browser window opens for sign-in. Pass `-Overwrite` only if the user confirms they want to replace an existing file — tell them when you do.

## 5. Confirm

Read the `OUTPUT=` and `FILES=` lines and report the SharePoint folder URL and the file count.

## Example

```
/toolkit-excel-upload push the Q3 sales pipeline to our team site
```
