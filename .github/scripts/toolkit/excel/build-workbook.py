#!/usr/bin/env python3
"""Build an Excel .xlsx workbook from a JSON content spec.

Usage:
    python build-workbook.py <spec.json> <output.xlsx>

The spec is a JSON object:
    {
      "sheets": [
        {
          "name": "Sheet name",
          "headers": ["Column A", "Column B"],
          "rows": [["a1", "b1"], ["a2", "b2"]]
        }
      ]
    }

Emits machine-readable KEY=value lines on success:
    OUTPUT=<absolute path to the .xlsx>
    SHEETS=<number of sheets>
    ROWS=<total data rows across all sheets>

Requires: openpyxl  (pip install openpyxl)
"""

import json
import os
import sys


def build(spec_path: str, output_path: str) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        print("ERROR=openpyxl not installed. Run: pip install openpyxl")
        sys.exit(1)

    with open(spec_path, encoding="utf-8") as spec_file:
        spec = json.load(spec_file)

    workbook = Workbook()
    workbook.remove(workbook.active)

    sheets = spec.get("sheets", [])
    total_rows = 0
    bold = Font(bold=True)

    for index, sheet_spec in enumerate(sheets):
        name = sheet_spec.get("name") or f"Sheet{index + 1}"
        worksheet = workbook.create_sheet(title=name[:31])

        headers = sheet_spec.get("headers", [])
        if headers:
            worksheet.append(headers)
            for cell in worksheet[1]:
                cell.font = bold

        for row in sheet_spec.get("rows", []):
            worksheet.append(row)
            total_rows += 1

    if not workbook.sheetnames:
        workbook.create_sheet(title="Sheet1")

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    workbook.save(output_path)

    print(f"OUTPUT={output_path}")
    print(f"SHEETS={len(workbook.sheetnames)}")
    print(f"ROWS={total_rows}")


def main() -> None:
    if len(sys.argv) != 3:
        print("ERROR=usage: python build-workbook.py <spec.json> <output.xlsx>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
