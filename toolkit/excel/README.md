---
title: "Excel"
parent: "Toolkit"
---

# 📈 Excel

Generate an Excel `.xlsx` workbook from a short content spec.

## How it works

This example shows the **prompt → script** pattern:

- **Prompt:** `/toolkit.excel.create` — turns your data into a JSON spec.
- **Template:** `.github/templates/toolkit/excel/toolkit.excel.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/excel/build-workbook.py` — reads the spec and builds the `.xlsx` with [`openpyxl`](https://openpyxl.readthedocs.io/).
- **Instruction:** `.github/instructions/toolkit/excel/toolkit.excel.instructions.md` — keeps generation in the script and rows aligned.

## Requirements

```bash
pip install openpyxl
```

## Output

```
toolkit/excel/YY-MM-DD-HHMM-short-description/
  spec.json
  workbook.xlsx
```

The `.xlsx` files are gitignored — only this README is tracked.

## Try it

```
/toolkit.excel.create a workbook with a sheet listing our team members and their roles
```
