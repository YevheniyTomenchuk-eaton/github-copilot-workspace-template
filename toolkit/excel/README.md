---
title: "Excel"
parent: "Toolkit"
---

# 📈 Excel

Generate an on-brand Excel workbook. The output is an `.xlsx` with a colored banner title, a frozen styled header, banded rows, number formatting, an auto-filter, and an optional totals row.

## How it works

- **Prompt:** `/toolkit.excel.create` — turns your data into a JSON spec and runs the build script.
- **Agent:** [`toolkit`](../../.github/agents/toolkit.agent.md) — loads the skill, writes the spec, and builds the workbook.
- **Skill:** [`office-documents`](../../.github/skills/office-documents/SKILL.md) — the brand system and the full sheet-spec schema.
- **Template:** `.github/templates/toolkit/excel/toolkit.excel.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/excel/build-workbook.py` — renders the styled workbook.
- **Instruction:** `.github/instructions/toolkit/excel/toolkit.excel.instructions.md` — output and naming rules.

## Column formats

Pick one token per column so numbers render correctly:

| Token | Renders |
|-------|---------|
| `text` | Plain text (default) |
| `number` | `#,##0` thousands |
| `currency` | `$#,##0` |
| `percent` | `0.8` → `80%` |
| `date` | `2026-08-15` → a real date cell |

## Output

Each workbook lands in its own timestamped folder here:

```text
toolkit/excel/YY-MM-DD-HHMM-short-description/
  spec.json
  workbook.xlsx
```

The generated files are gitignored — only this README is tracked. Run `pip install openpyxl` once before the first build.

## Try it

Open Copilot Chat and run:

```text
/toolkit.excel.create a Q3 sales pipeline — deal, owner, value, probability, close date, with a totals row
```
