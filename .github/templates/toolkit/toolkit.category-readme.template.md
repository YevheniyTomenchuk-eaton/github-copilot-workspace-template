---
title: "{Display Name}"
parent: "Toolkit"
---

# {emoji} {Display Name}

{One-paragraph purpose. Facts only — say what the category generates and what the output looks like.}

## Prompts

| Prompt | What it does |
|--------|--------------|
| `toolkit.{category}.{action}` | {What it builds, in one line} |
| `toolkit.{category}.upload` | Upload the generated {file} to a SharePoint folder you choose |

{Optional: a category-specific reference table — slide layouts, column formats, section blocks. Keep it only if it helps the reader fill the spec.}

## Sources

| What | Where |
|------|-------|
| Brand system + spec schema | [`office-documents`](../../.github/skills/office-documents/SKILL.md) |
| Spec template | `.github/templates/toolkit/{category}/...` |
| Generator script | `.github/scripts/toolkit/{category}/...` |
| Upload script | [`sharepoint-upload`](../../.github/skills/sharepoint-upload/SKILL.md) |

## Outputs

| What | Where |
|------|-------|
| Per-run folder | `toolkit/{category}/YY-MM-DD-HHMM-short-description/` |
| {File} | `toolkit/{category}/YY-MM-DD-HHMM-short-description/{file}` |

All generated content under `toolkit/{category}/` is gitignored. Only this README is tracked. Run `pip install {package}` once before the first build.

## Folder layout

```text
toolkit/{category}/
└── YY-MM-DD-HHMM-short-description/
    ├── spec.json        # the spec the generator built from
    └── {file}           # the styled output
```
