---
name: toolkit-excel-create
description: "Create an on-brand Excel .xlsx workbook from a content spec. Use when the user says 'make a spreadsheet', 'build a workbook', 'budget', 'tracker', or '/toolkit-excel-create'."
---

# Create Workbook

Turn data into an on-brand Excel workbook. You write a JSON spec; the build script renders the banner title, frozen styled header, banded rows, number formatting, auto-filter, and totals.

## 1. Load the rules

Read these before writing anything:

1. [`office-documents`](../office-documents/SKILL.md) skill — the brand system and the full Excel spec schema (section 3).
2. [`toolkit.excel.instructions.md`](../../instructions/toolkit/excel/toolkit.excel.instructions.md) — output layout and naming.
3. [`toolkit.instructions.md`](../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Gather the content

Ask only for what changes the workbook: what is being tracked, the columns, and whether a totals row is wanted. Pick a `formats` token per column (`text`, `number`, `currency`, `percent`, `date`) so numbers render correctly.

## 3. Write the spec

1. Copy [`toolkit.excel.template.json`](../../templates/toolkit/excel/toolkit.excel.template.json) as the starting point.
2. Fill each sheet's `name`, `title` banner, `headers`, `formats`, `rows`, and optional `totals`.
3. Every row must match the header length. Percents are fractions (`0.8` → 80%); dates are `YYYY-MM-DD`.
4. Save to a timestamped folder: `toolkit/excel/YY-MM-DD-HHMM-short-description/spec.json`.

## 4. Build the workbook

```
python .github/scripts/toolkit/excel/build-workbook.py toolkit/excel/YY-MM-DD-HHMM-short-description/spec.json toolkit/excel/YY-MM-DD-HHMM-short-description/workbook.xlsx
```

If the script prints `ERROR=openpyxl not installed`, tell the user to run `pip install openpyxl` and retry.

## 5. Confirm

Read the `OUTPUT=`, `SHEETS=`, and `ROWS=` lines and report the path and counts.

## Example

```
/toolkit-excel-create a Q3 sales pipeline — deal, owner, value, probability, close date, with a totals row
```
