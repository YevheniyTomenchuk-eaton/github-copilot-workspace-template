---
title: "Toolkit"
nav_order: 8
has_toc: false
---

# 🛠️ Toolkit

AI-powered workspace for creating Office documents. Each category exposes a prompt — describe what you need and get a finished, on-brand file: a slide deck, a workbook, a report, or an email draft. A **prompt** drives a **script** that fills a **template**, governed by an **instruction** file, with a shared **skill** for the design system and a dedicated **agent** to run the job.

```bash
pip install python-pptx openpyxl python-docx
```

## Categories

| Category | What it generates | Highlights |
|---------|-------------------|------------|
| [Presentation](presentation/README.md) | A 16:9 PowerPoint `.pptx` deck | Branded title slide, section dividers, two-column & quote layouts, slide-number footers |
| [Excel](excel/README.md) | An Excel `.xlsx` workbook | Banner title, frozen styled header, banded rows, currency/percent/date formats, auto-filter, totals |
| [Word](word/README.md) | A Word `.docx` document | Cover page, brand-colored headings, callout boxes, banded tables, page-number footer |
| [Email](email/README.md) | An Outlook-ready `.eml` draft | Brand header band, clean typography, styled signature divider — opens with a Send button |

## Shared design system

Every document shares one design system so a deck, a workbook, a report, and an email stay consistent. The palette, type scale, layout rules, and the JSON spec each generator accepts all live in one place:

- **Skill** — [`office-documents`](../.github/skills/office-documents/SKILL.md) holds the brand system and every spec schema. Prompts and the agent load it on demand.
- **Agent** — [`toolkit`](../.github/agents/toolkit.agent.md) loads the skill, picks the right prompt, and turns a request into a finished file.

## The pattern they share

Every category wires together the same pieces, mirroring the repo under `.github/`:

- **Instruction** (`.github/instructions/toolkit/<name>/`) — rules that auto-apply when you work in `toolkit/<name>/`.
- **Prompt** (`.github/prompts/toolkit/<name>/`) — the `/` command you invoke to start the job.
- **Template** (`.github/templates/toolkit/<name>/`) — the spec skeleton the output is built from.
- **Script** (`.github/scripts/toolkit/<name>/`) — the deterministic generator that owns every color and border.
- **Skill + Agent** — the shared design system and the agent that runs it.
- **Output** (`toolkit/<name>/`) — where the generated file lands (gitignored; only the README is tracked).

Copy any one of these folders as the starting point for your own toolkit category.

## Managing toolkits

Two prompts automate the wiring so a new category is registered in **every** required place — published README, hub entry, instructions, prompts folder, optional templates, `.gitignore`, and the Jekyll `exclude:` in both config files. Miss one and the toolkit breaks silently (404, missing sidebar entry, generated files committed by mistake).

| Prompt | What it does |
|--------|--------------|
| `/toolkit.create` | Create and register a brand-new toolkit category in all seven places |
| `/toolkit.update` | Modify an existing toolkit — add, rename, or remove a prompt, change the output pattern, refresh the README, or rename/remove the whole category — and re-sync every registration point |

Both follow the rules in [`.github/instructions/toolkit/toolkit.instructions.md`](../.github/instructions/toolkit/toolkit.instructions.md) (the "Toolkit Anatomy" section).
