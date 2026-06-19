---
applyTo: "toolkit/excel/**"
---

# Excel Instructions

Generate Excel `.xlsx` workbooks by writing a JSON content spec and calling the build script. Never construct the binary `.xlsx` by hand.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/excel/toolkit.excel.template.json`
- **Script (generator):** `.github/scripts/toolkit/excel/build-workbook.py`

## Spec format

The spec is a JSON object with a `sheets` array. Each sheet has a `name`, optional `headers`, and a `rows` array of equal-length value lists:

```json
{
  "sheets": [
    {
      "name": "Summary",
      "headers": ["Item", "Count"],
      "rows": [["Apples", 12], ["Pears", 7]]
    }
  ]
}
```

## Rules

- **Deterministic generation belongs in the script.** The prompt turns the user's request into a valid spec and calls the script — never hand-author `.xlsx` contents.
- **Every row must match the header length.** Ragged rows produce a misaligned sheet.
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

The script prints `OUTPUT=<path>`, `SHEETS=<n>`, and `ROWS=<n>` on success. Parse those lines to confirm the result, then report the output path to the user.
