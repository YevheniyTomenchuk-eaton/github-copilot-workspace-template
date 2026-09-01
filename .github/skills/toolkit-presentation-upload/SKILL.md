---
name: toolkit-presentation-upload
description: "Upload a generated PowerPoint .pptx to a SharePoint folder you choose. Use when the user says 'upload the deck to SharePoint', 'push the pptx', or '/toolkit-presentation-upload'."
---

# Upload Presentation to SharePoint

Push a built PowerPoint deck to a SharePoint folder. The site URL and folder are supplied by the user — nothing is hardcoded.

## 1. Load the rules

Read these before running anything:

1. [`sharepoint-upload`](../sharepoint-upload/SKILL.md) skill — the uploader, its parameters, and the overwrite policy.
2. [`toolkit.instructions.md`](../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Pick the file

Find the `.pptx` to upload — usually the newest one under `toolkit/presentation/YY-MM-DD-HHMM-short-description/presentation.pptx`. If more than one exists, ask which one. Build it first with `/toolkit-presentation-create` if none exists yet.

## 3. Ask for the destination

Ask the user for both, and never guess a URL:

- **Site URL** — e.g. `https://contoso.sharepoint.com/sites/MyTeam`.
- **Target folder** — server-relative, e.g. `/sites/MyTeam/Shared Documents/General/Decks`.

## 4. Upload

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .github/scripts/toolkit/sharepoint-upload/upload-to-sharepoint.ps1 -LocalPath "toolkit/presentation/YY-MM-DD-HHMM-short-description/presentation.pptx" -SiteUrl "<site-url>" -TargetFolder "<target-folder>" -CreateFolder
```

A browser window opens for sign-in. Pass `-Overwrite` only if the user confirms they want to replace an existing file — tell them when you do.

## 5. Confirm

Read the `OUTPUT=` and `FILES=` lines and report the SharePoint folder URL and the file count.

## Example

```
/toolkit-presentation-upload push the Q3 review deck to our team site
```
