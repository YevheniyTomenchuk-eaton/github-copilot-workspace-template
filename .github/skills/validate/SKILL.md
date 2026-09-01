---
name: validate
description: "Run all CI validation checks locally. Use when: user says 'validate', wants to check for errors before shipping, or needs to verify the site content is clean."
---

# Validate — Run All CI Checks Locally

Run each validation script below **sequentially** in the terminal. Collect pass/fail results, then present a summary.

## Scripts to Run

Run all 7 Python scripts from the repository root. Each script exits 0 on success, non-zero on failure.

```
python .github/scripts/check-github-pages.py .
python .github/scripts/check-github-structure.py .
python .github/scripts/check-markdown-links.py .
python .github/scripts/check-markdown-tables.py .
python .github/scripts/check-mermaid-diagrams.py .
python .github/scripts/check-customization-inline-logic.py .
python .github/scripts/check-powershell-conventions.py .
```

## Encoding Check

The 8th CI check (UTF-8 no BOM + CRLF line endings) runs inline in the workflow. [.github/scripts/check-encoding.ps1](../../scripts/check-encoding.ps1) reproduces it locally — by default it inspects all changed `.md` files since HEAD:

```powershell
& .github\scripts\check-encoding.ps1
```

It echoes `FAIL=<file> (<reason>)` for each offending file plus `CHECKED=`, `FAILED=`, and `RESULT=pass|fail`, and exits non-zero on any failure. If no files are staged/modified (`CHECKED=0`), mark this check as ✅. Pass `-Path` to check explicit files or folders instead of the changed set.

## Summary Table

After all scripts finish, present results in this format:

| Check | Result |
|-------|--------|
| GitHub Pages (front matter, hierarchy, navigation) | ✅ or ❌ |
| GitHub Structure (folder conventions) | ✅ or ❌ |
| Markdown Links (broken references) | ✅ or ❌ |
| Markdown Tables (formatting) | ✅ or ❌ |
| Mermaid Diagrams (syntax, standards) | ✅ or ❌ |
| Customization Inline Logic (no inlined scripts or skeletons) | ✅ or ❌ |
| PowerShell Conventions (launch flags, param guards, ASCII, Git capture) | ✅ or ❌ |
| Encoding (UTF-8 no BOM + CRLF) | ✅ or ❌ |

For any ❌ failures, list the specific errors reported by that script beneath the table.
