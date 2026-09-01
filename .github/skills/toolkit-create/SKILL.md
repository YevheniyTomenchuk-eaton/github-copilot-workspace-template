---
name: toolkit-create
description: "Create and register a new toolkit category — README, instructions, action skills, gitignore, Jekyll exclude, hub entry"
---

# Create New Toolkit Category

## Task

Add a new toolkit category and register it in **every** place required for it to work on GitHub Pages, in Copilot Chat, and on disk. Skipping any step breaks the toolkit silently (404, missing sidebar entry, generated files committed by mistake, broken incremental builds).

## Context Loading

1. Read `.github/instructions/toolkit/toolkit.instructions.md` — full toolkit anatomy, writing style, linking rules.
2. Read `toolkit/README.md` — the hub page where the new category must appear.
3. Read `.gitignore` (toolkit section) — to understand the existing patterns.
4. Read `_config.yml` and `_config_local.yml` (`exclude:` block) — to understand the existing Jekyll exclude patterns.
5. Read one existing toolkit README as a model:
   - Single-file output, no script (template only) → `toolkit/email/README.md`
   - Script-driven output (the skill writes a spec, a script builds the file) → `toolkit/word/README.md`
6. Read `.github/instructions/github/skills/github.skills.instructions.md` — the rules for authoring the action skills in step 4.

## User Input

Before doing anything, collect from the user (ask interactively if any answer is missing):

| Field | Required | Example |
| ----- | -------- | ------- |
| Category slug (kebab-case) | ✅ | `release-notes` |
| Display name | ✅ | `Release Notes` |
| Emoji | ✅ | `📝` |
| One-line purpose | ✅ | `Generate release notes from a list of changes` |
| Actions (list of `{action}` + one-liner) | ✅ | `create` → build notes from a changelog |
| Output pattern | ✅ | `toolkit/release-notes/YY-MM-DD-HHMM-{slug}/release-notes.md` |
| Source inputs | optional | a changelog file, a list of items |
| Needs dedicated agent? | optional | usually no |
| Reuses existing skills? | optional | list skill names |
| Templates needed? | optional | list template files |
| Scripts needed? | optional | list `.py` / `.ps1` files |

Refuse to proceed if the slug already exists under `toolkit/`, `.github/instructions/toolkit/`, or as a `.github/skills/toolkit-{slug}-*/` folder.

## Registration Steps

Execute **all seven** in order. After each step, confirm the file exists.

### 1. Published page — `toolkit/{slug}/README.md`

Create the folder and README using the unified template from `.github/instructions/toolkit/toolkit.instructions.md` (section "Toolkit Anatomy → 1. Published page"). Frontmatter:

```yaml
---
title: "{Display Name}"
parent: "Toolkit"
---
```

Include the mandatory sections: How it works, Output, Try it. Use simple sentences (rule from `toolkit.instructions.md`).

### 2. Hub registration — `toolkit/README.md`

Insert a row in the `## Examples` table:

```markdown
| [{Display Name}]({slug}/README.md) | {what it generates} | {how it works} |
```

### 3. Instructions — `.github/instructions/toolkit/{slug}/toolkit.{slug}.instructions.md`

```yaml
---
applyTo: "toolkit/{slug}/**"
---
```

Body: format rules, naming, output layout, edge cases specific to the category. Keep it short — defer general rules to `toolkit.instructions.md`.

### 4. Skills — `.github/skills/toolkit-{slug}-{action}/SKILL.md`

One skill folder per action collected from the user, run as `/toolkit-{slug}-{action}`. Skills sit **flat** under `.github/skills/` — the kebab-case folder name encodes the mirrored path, so never create a `toolkit/` subfolder there. Prompts are retired; a `*.prompt.md` file fails the structure check with `prompt-file-retired`. Frontmatter:

```yaml
---
name: toolkit-{slug}-{action}
description: "{What it does, and WHEN to use it — this text is the auto-invocation trigger}"
---
```

`name` must match the folder name exactly. Body sections (in order): `## Task`, `## Context Loading` (numbered file reads — always include `toolkit.instructions.md` and the new category instructions), `## {Action} Steps`, `## User Input` with an example.

### 5. Templates — `.github/templates/toolkit/{slug}/` (only if requested)

File name: `toolkit.{slug}.{descriptor}.template.{ext}`. The word `template` appears **exactly once**, as the suffix.

### 6. `.gitignore`

Append to the toolkit block. Default shape ignores everything but the README:

```gitignore
toolkit/{slug}/*
!toolkit/{slug}/README.md
```

When the outputs are single files of a known extension, mirror the existing per-extension lines instead (e.g. `toolkit/{slug}/*.pdf`).

### 7. Jekyll exclude — `_config.yml` and `_config_local.yml`

Add patterns under `exclude:` in **both** files. Match what the toolkit actually produces:

| Output style | Exclude pattern |
| ------------ | --------------- |
| Single file (`*.eml`, `*.xlsx`, `*.pdf`, `*.pptx`, `*.docx`) | `toolkit/{slug}/*.{ext}` |
| Timestamped folder (`YY-MM-...`) | `toolkit/{slug}/*/` |
| Mixed | list each |

After editing, delete `.jekyll-cache/` and `.jekyll-metadata`:

```powershell
Remove-Item -Recurse -Force .jekyll-cache, .jekyll-metadata -ErrorAction SilentlyContinue
```

Tell the user to restart the `Pages: Start Server` task — Jekyll reads `_config.yml` only at startup.

## Verification

After all seven steps, confirm:

1. `Test-Path toolkit/{slug}/README.md` → True
2. `Test-Path .github/instructions/toolkit/{slug}/toolkit.{slug}.instructions.md` → True
3. Every action skill exists at `.github/skills/toolkit-{slug}-{action}/SKILL.md`, with `name` matching its folder
4. `grep_search` for the new slug in `.gitignore` returns the expected lines
5. `grep_search` for the new slug in `_config.yml` and `_config_local.yml` returns matching exclude patterns
6. The new row appears in `toolkit/README.md`

## Edge Cases

- **Slug collision.** If a folder with the same slug exists anywhere under `toolkit/`, `.github/instructions/toolkit/`, or as a `.github/skills/toolkit-{slug}-*/` folder, stop and ask the user for a different slug.
- **Sidebar parent.** `parent: "Toolkit"` must match the exact `title` in `toolkit/README.md`. Don't invent.
- **Don't link to bare folders.** Always `folder/README.md`. Never `folder/`. Never `(.)`.
- **Custom agent.** If the user said they need a dedicated agent that doesn't exist, create it under `.github/agents/{name}.agent.md` and name it in the category README and in the action skills that rely on it.
- **Encoding.** Write every file UTF-8 without BOM and CRLF line endings. If a file ends up with mixed encoding (visible as `?` in place of emojis), rewrite it via PowerShell:
  ```powershell
  [System.IO.File]::WriteAllText((Resolve-Path $path), $content, (New-Object System.Text.UTF8Encoding $false))
  ```
- **Don't commit yet.** Toolkit creation is local — let the user invoke `/ship` when they're ready.

## Example

> *"Create a new toolkit called `release-notes` (📝 Release Notes) that generates release notes from a changelog. One action `create` — the `/toolkit-release-notes-create` skill — that reads a changelog file and outputs `release-notes.md` into a timestamped folder."*
