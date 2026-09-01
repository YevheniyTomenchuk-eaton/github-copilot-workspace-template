---
title: "Word"
parent: "Toolkit"
---

# 📄 Word

Generate an on-brand Word document, then upload it to SharePoint. The output is a `.docx` with a cover page, brand-colored headings, lead lines, callout boxes, banded tables, and a page-number footer.

## Skills

| Skill | What it does |
|-------|--------------|
| `/toolkit-word-create` | Turn a topic into a JSON spec and build the styled `.docx` |
| `/toolkit-word-upload` | Upload the generated `.docx` to a SharePoint folder you choose |

## Section building blocks

Each section starts with a `heading`; add any of these where they help:

| Field | Renders |
|-------|---------|
| `lead` | A larger intro line under the heading |
| `paragraphs` | Body prose in full sentences |
| `callout` | A shaded accent box for the one thing to remember |
| `bullets` | A bulleted list |
| `table` | A table with a shaded header and banded rows |

## Sources

| What | Where |
|------|-------|
| Brand system + document spec schema | [`office-documents`](../../.github/skills/office-documents/SKILL.md) |
| Spec template | `.github/templates/toolkit/word/toolkit.word.template.json` |
| Generator script | `.github/scripts/toolkit/word/build-document.py` |
| Upload script | [`sharepoint-upload`](../../.github/skills/sharepoint-upload/SKILL.md) |

## Outputs

| What | Where |
|------|-------|
| Per-run folder | `toolkit/word/YY-MM-DD-HHMM-short-description/` |
| Document | `toolkit/word/YY-MM-DD-HHMM-short-description/document.docx` |

All generated content under `toolkit/word/` is gitignored. Only this README is tracked. Run `pip install python-docx` once before the first build.

## Folder layout

```text
toolkit/word/
└── YY-MM-DD-HHMM-short-description/
    ├── spec.json        # the spec the generator built from
    └── document.docx    # the styled document
```
