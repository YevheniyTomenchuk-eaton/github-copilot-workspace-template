---
applyTo: "toolkit/excel/**"
---

# Excel Instructions

Generate Excel `.xlsx` workbooks by writing a JSON content spec and calling the build script. Never construct the binary `.xlsx` by hand.

## Design system & spec schema

The brand palette and the **full spec schema** (sheet `title` banner, `formats` tokens, `totals` row) live in the [`office-documents`](../../../skills/office-documents/SKILL.md) skill, section 3. Read it before writing a spec.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/excel/toolkit.excel.template.json`
- **Script (generator):** `.github/scripts/toolkit/excel/build-workbook.py`

## Rules

- **Deterministic styling belongs in the script.** The prompt turns the request into a valid spec — never hand-author `.xlsx` contents.
- **Every row must match the header length.** Ragged rows produce a misaligned sheet.
- **Pick a `formats` token per column** (`text`, `number`, `currency`, `percent`, `date`). Percents are fractions (`0.8` → 80%); dates are `YYYY-MM-DD`.
- **Sheet names are 31 characters or fewer** (Excel limit; the script truncates).
- **Validate the spec is JSON** before calling the script.
- **Requires** `openpyxl` (`pip install openpyxl`).

## Output Structure

Each workbook gets its own timestamped folder:

```
toolkit/excel/YY-MM-DD-HHMM-short-description/
  spec.json
  workbook.xlsx
```

The `.xlsx` files are gitignored — only the README is tracked.

## Running the script

```
python .github/scripts/toolkit/excel/build-workbook.py <spec.json> <output.xlsx>
```

The script prints `OUTPUT=<path>`, `SHEETS=<n>`, and `ROWS=<n>` on success. Parse those lines and report the output path.
