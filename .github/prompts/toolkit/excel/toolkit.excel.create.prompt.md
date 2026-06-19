---
description: "Create an Excel .xlsx workbook from a content spec. Use when the user says 'make a spreadsheet', 'build an Excel file', or '/toolkit.excel.create'."
agent: "agent"
---

# Create Workbook

Generate an Excel workbook by writing a JSON spec and calling the build script. Follow the rules in [`toolkit.excel.instructions.md`](../../../instructions/toolkit/excel/toolkit.excel.instructions.md).

## 1. Gather the data

Ask the user what the workbook should contain — the sheets, their columns, and the rows of data. If the data comes from a file or table, read it first.

## 2. Write the spec

1. Copy [`toolkit.excel.template.json`](../../../templates/toolkit/excel/toolkit.excel.template.json) as the starting point.
2. Fill in the `sheets` array. Ensure every row has the same number of values as its `headers`.
3. Save it to a timestamped folder: `toolkit/excel/YY-MM-DD-HHMM-short-description/spec.json`.

## 3. Build the workbook

Run the generator:

```
python .github/scripts/toolkit/excel/build-workbook.py toolkit/excel/YY-MM-DD-HHMM-short-description/spec.json toolkit/excel/YY-MM-DD-HHMM-short-description/workbook.xlsx
```

If the script prints `ERROR=openpyxl not installed`, tell the user to run `pip install openpyxl` and retry.

## 4. Confirm

Read the `OUTPUT=`, `SHEETS=`, and `ROWS=` lines from the script output. Report the output path and totals to the user.
