---
description: "Update an existing toolkit category — add/rename/remove a prompt, refresh README, keep gitignore + Jekyll exclude in sync"
agent: agent
---

# Update Existing Toolkit Category

## Task

Modify an existing toolkit. The update may touch one or more of: prompts, instructions, templates, agents, skills, output patterns, gitignore, Jekyll exclude, hub description, README structure. The goal is to keep **all seven registration places** consistent (see "Toolkit Anatomy" in `.github/instructions/toolkit/toolkit.instructions.md`).

## Context Loading

1. Read `.github/instructions/toolkit/toolkit.instructions.md` — full anatomy, writing style, linking rules.
2. Read `toolkit/{slug}/README.md` — current state.
3. Read `.github/instructions/toolkit/{slug}/` — every instruction file.
4. List `.github/prompts/toolkit/{slug}/` — every existing prompt.
5. List `.github/templates/toolkit/{slug}/` and `.github/scripts/toolkit/{slug}/` if they exist.
6. `grep_search` for `toolkit/{slug}` in `.gitignore`, `_config.yml`, `_config_local.yml`, and `toolkit/README.md` to see current registration.

## User Input

Identify which kind of update the user wants. Ask if unclear:

| Update kind | What to do |
| ----------- | ---------- |
| **Add a prompt** | Create `.github/prompts/toolkit/{slug}/toolkit.{slug}.{action}.prompt.md`; add a bullet to the README "How it works" section |
| **Rename a prompt** | Move file; update the README; search the workspace for old name with `grep_search` and update any references |
| **Remove a prompt** | Delete file; remove the README reference; verify no other prompts/skills reference it |
| **Add/remove an agent or skill** | Update the README; if adding a new agent, create `.github/agents/{name}.agent.md` |
| **Change output pattern** | Update README "Output"; update `.gitignore`; update `exclude:` in both `_config.yml` and `_config_local.yml` |
| **Change source inputs** | Update README "How it works"; verify referenced paths exist |
| **Refresh README** | Re-align to the unified template (see anatomy section); preserve all factual content |
| **Rename the category** | Full slug migration — see "Renaming" below |
| **Remove the category** | Full teardown — see "Removing" below |

## Standard Steps

For any non-rename / non-remove update:

### 1. Make the requested change

Edit only what the user asked for. Do not refactor unrelated content.

### 2. Sync the README

After any change, the README must still reflect reality:

- **How it works** must list every prompt in `.github/prompts/toolkit/{slug}/`, plus the template/script/instruction it uses.
- **Output** must list the file pattern the prompts actually produce.
- **Try it** must show a working example invocation.

### 3. Sync `.gitignore`

If the output pattern changed, update the toolkit block. Default shape:

```gitignore
toolkit/{slug}/*
!toolkit/{slug}/README.md
```

### 4. Sync `_config.yml` and `_config_local.yml`

If the output pattern changed, update the `exclude:` block in **both** files. Match what the toolkit actually produces — wildcards or timestamped folders. Then:

```powershell
Remove-Item -Recurse -Force .jekyll-cache, .jekyll-metadata -ErrorAction SilentlyContinue
```

Tell the user to restart the `Pages: Start Server` task — Jekyll reads config only at startup.

### 5. Sync `toolkit/README.md`

If the one-line purpose, slug, or display name changed, update the row in the `## Examples` table.

## Renaming the Category

If the slug or display name changes, the rename touches every registration place listed in the Toolkit Anatomy plus a few collateral updates:

1. `toolkit/{old}/` → `toolkit/{new}/` (folder)
2. Inside `toolkit/{new}/README.md`: update `title:` (display name only; `parent: "Toolkit"` stays).
3. `.github/instructions/toolkit/{old}/` → `.github/instructions/toolkit/{new}/`; rename every `toolkit.{old}.*.instructions.md` → `toolkit.{new}.*.instructions.md`; update each file's `applyTo: "toolkit/{new}/**"`.
4. `.github/prompts/toolkit/{old}/` → `.github/prompts/toolkit/{new}/`; rename every `toolkit.{old}.{action}.prompt.md` → `toolkit.{new}.{action}.prompt.md`; update every `Context Loading` step that references the old paths.
5. `.github/templates/toolkit/{old}/` and `.github/scripts/toolkit/{old}/` → rename folder + every file inside; the word `template` in template files still appears exactly once as the suffix.
6. `.gitignore`: replace `toolkit/{old}/*` and `!toolkit/{old}/README.md` with the new slug.
7. `_config.yml` + `_config_local.yml`: replace every `toolkit/{old}/...` exclude line.
8. `toolkit/README.md`: update the table row (link target + display name).
9. `grep_search` for `{old}` across the whole workspace — fix every cross-link in other toolkit READMEs, the home `README.md`, and any prompt that referenced the old slug.

## Removing the Category

Delete every artifact:

1. `toolkit/{slug}/` folder — including the published README.
2. Hub row in `toolkit/README.md`.
3. `.github/instructions/toolkit/{slug}/` folder.
4. `.github/prompts/toolkit/{slug}/` folder.
5. `.github/templates/toolkit/{slug}/` folder (if present).
6. `.github/scripts/toolkit/{slug}/` folder (if present).
7. `.gitignore` lines for the slug.
8. `_config.yml` + `_config_local.yml` exclude lines for the slug.

Then `grep_search` for the slug to confirm zero leftover references.

## Verification

After any update, run:

1. `grep_search` for the slug across `.gitignore`, `_config.yml`, `_config_local.yml`, `toolkit/README.md` — all four should be in sync.
2. `grep_search` for old names (after rename / remove) — should return zero matches.
3. Confirm `toolkit/{slug}/README.md` still uses the unified template structure (How it works, Output, Try it as a minimum).
4. If config files changed, remind the user to restart `Pages: Start Server`.

## Edge Cases

- **Encoding.** Preserve UTF-8 without BOM and CRLF. If a file gets corrupted, rewrite via:
  ```powershell
  [System.IO.File]::WriteAllText((Resolve-Path $path), $content, (New-Object System.Text.UTF8Encoding $false))
  ```
- **Don't link to bare folders.** Always `folder/README.md`. Never `folder/` and never `(.)`.
- **Don't commit yet.** Updates stay local — let the user invoke `/ship` when ready.

## Example

> *"In the `email` toolkit, add a new prompt `forward-with-context` that takes a forwarded email and enriches it with links."*
>
> *"Rename the `word` toolkit to `documents`."*
>
> *"Remove the `excel` toolkit — we don't need spreadsheets."*
