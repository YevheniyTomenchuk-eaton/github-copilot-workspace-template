---
title: "Toolkit"
nav_order: 8
has_toc: false
---

# 🛠️ Toolkit

AI-powered workspace for creating Office documents. Each category exposes a set of **prompts** — pick one, describe what you need, get a finished, on-brand file: a slide deck, a workbook, a report, or an email draft.

```bash
pip install python-pptx openpyxl python-docx
```

## How to use a prompt

1. Open the category page below to see its prompts and what each one does.
2. In Copilot Chat, invoke the prompt by its name (e.g., `toolkit.word.create`) and describe the task.
3. The prompt loads the right instructions, agent, skill, and template automatically.

## 📂 Categories

| Category | Purpose |
|----------|---------|
| [Presentation](presentation/README.md) | Build a 16:9 PowerPoint deck, then upload it to a SharePoint folder you choose |
| [Excel](excel/README.md) | Build an Excel workbook with formatted columns and totals, then upload it to SharePoint |
| [Word](word/README.md) | Build a Word document with a cover page and styled sections, then upload it to SharePoint |
| [Email](email/README.md) | Build an Outlook-ready `.eml` draft that opens with a Send button |

## Shared design system

Every document shares one design system so a deck, a workbook, a report, and an email stay consistent. The palette, type scale, layout rules, and the JSON spec each generator accepts all live in one place:

- **Skill** — [`office-documents`](../.github/skills/office-documents/SKILL.md) holds the brand system and every spec schema. Prompts and the agent load it on demand.
- **Skill** — [`sharepoint-upload`](../.github/skills/sharepoint-upload/SKILL.md) pushes a finished file to any SharePoint folder you name at run time.
- **Agent** — [`toolkit`](../.github/agents/toolkit.agent.md) loads the skills, picks the right prompt, and turns a request into a finished file.

## The pattern they share

Every category wires together the same pieces, mirroring the repo under `.github/`:

- **Instruction** (`.github/instructions/toolkit/<name>/`) — rules that auto-apply when you work in `toolkit/<name>/`.
- **Prompt** (`.github/prompts/toolkit/<name>/`) — the `/` command you invoke to start the job.
- **Template** (`.github/templates/toolkit/<name>/`) — the spec skeleton the output is built from.
- **Script** (`.github/scripts/toolkit/<name>/`) — the deterministic generator that owns every color and border.
- **Skill + Agent** — the shared design system and the agent that runs it.
- **Output** (`toolkit/<name>/`) — where the generated file lands (gitignored; only the README is tracked).

Copy any one of these folders as the starting point for your own toolkit category.

## Meta prompts

Two prompts automate the wiring so a new category is registered in **every** required place — published README, hub entry, instructions, prompts folder, optional templates, `.gitignore`, and the Jekyll `exclude:` in both config files. Miss one and the toolkit breaks silently (404, missing sidebar entry, generated files committed by mistake).

| Prompt | What it does |
|--------|--------------|
| `/toolkit.create` | Create and register a brand-new toolkit category in all seven places |
| `/toolkit.update` | Modify an existing toolkit — add, rename, or remove a prompt, change the output pattern, refresh the README, or rename/remove the whole category — and re-sync every registration point |

Both follow the rules in [`.github/instructions/toolkit/toolkit.instructions.md`](../.github/instructions/toolkit/toolkit.instructions.md) (the "Toolkit Anatomy" section). New category READMEs are copied from [`toolkit.category-readme.template.md`](../.github/templates/toolkit/toolkit.category-readme.template.md).

## What is published vs. local-only

Only category `README.md` files are tracked in git and published to GitHub Pages. Every generated file — decks, workbooks, documents, email drafts — is produced **locally** in `toolkit/<category>/` and is gitignored. Uploading a file to SharePoint sends that local copy; it never commits anything.
