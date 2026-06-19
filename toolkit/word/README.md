---
title: "Word"
parent: "Toolkit"
---

# 📄 Word

Generate an on-brand Word document. The output is a `.docx` with a cover page, brand-colored headings, lead lines, callout boxes, banded tables, and a page-number footer.

## How it works

- **Prompt:** `/toolkit.word.create` — turns your topic into a JSON spec and runs the build script.
- **Agent:** [`toolkit`](../../.github/agents/toolkit.agent.md) — loads the skill, writes the spec, and builds the document.
- **Skill:** [`office-documents`](../../.github/skills/office-documents/SKILL.md) — the brand system and the full document-spec schema.
- **Template:** `.github/templates/toolkit/word/toolkit.word.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/word/build-document.py` — renders the styled document.
- **Instruction:** `.github/instructions/toolkit/word/toolkit.word.instructions.md` — output and naming rules.

## Section building blocks

Each section starts with a `heading`; add any of these where they help:

| Field | Renders |
|-------|---------|
| `lead` | A larger intro line under the heading |
| `paragraphs` | Body prose in full sentences |
| `callout` | A shaded accent box for the one thing to remember |
| `bullets` | A bulleted list |
| `table` | A table with a shaded header and banded rows |

## Output

Each document lands in its own timestamped folder here:

```text
toolkit/word/YY-MM-DD-HHMM-short-description/
  spec.json
  document.docx
```

The generated files are gitignored — only this README is tracked. Run `pip install python-docx` once before the first build.

## Try it

Open Copilot Chat and run:

```text
/toolkit.word.create a one-page vendor evaluation report comparing three suppliers with a recommendation
```
