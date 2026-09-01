---
title: "Excel"
parent: "Toolkit"
---

# 📈 Excel

Generate an on-brand Excel workbook, then upload it to SharePoint. The output is an `.xlsx` with a colored banner title, a frozen styled header, banded rows, number formatting, an auto-filter, and an optional totals row.

## Skills

| Skill | What it does |
|-------|--------------|
| `/toolkit-excel-create` | Turn your data into a JSON spec and build the styled `.xlsx` |
| `/toolkit-excel-upload` | Upload the generated `.xlsx` to a SharePoint folder you choose |

## Column formats

Pick one token per column so numbers render correctly:

| Token | Renders |
|-------|---------|
| `text` | Plain text (default) |
| `number` | `#,##0` thousands |
| `currency` | `$#,##0` |
| `percent` | `0.8` → `80%` |
| `date` | `2026-08-15` → a real date cell |

## Sources

| What | Where |
|------|-------|
| Brand system + sheet spec schema | [`office-documents`](../../.github/skills/office-documents/SKILL.md) |
| Spec template | `.github/templates/toolkit/excel/toolkit.excel.template.json` |
| Generator script | `.github/scripts/toolkit/excel/build-workbook.py` |
| Upload script | [`sharepoint-upload`](../../.github/skills/sharepoint-upload/SKILL.md) |

## Outputs

| What | Where |
|------|-------|
| Per-run folder | `toolkit/excel/YY-MM-DD-HHMM-short-description/` |
| Workbook | `toolkit/excel/YY-MM-DD-HHMM-short-description/workbook.xlsx` |

All generated content under `toolkit/excel/` is gitignored. Only this README is tracked. Run `pip install openpyxl` once before the first build.

## Folder layout

```text
toolkit/excel/
└── YY-MM-DD-HHMM-short-description/
    ├── spec.json        # the spec the generator built from
    └── workbook.xlsx    # the styled workbook
```
