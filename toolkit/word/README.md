---
title: "Word"
parent: "Toolkit"
---

# 📝 Word

Generate a Word `.docx` document from a short content spec.

## How it works

This example shows the **prompt → script** pattern:

- **Prompt:** `/toolkit.word.create` — turns your topic into a JSON spec.
- **Template:** `.github/templates/toolkit/word/toolkit.word.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/word/build-document.py` — reads the spec and builds the `.docx` with [`python-docx`](https://python-docx.readthedocs.io/).
- **Instruction:** `.github/instructions/toolkit/word/toolkit.word.instructions.md` — keeps generation in the script and content in real prose.

## Requirements

```bash
pip install python-docx
```

## Output

```
toolkit/word/YY-MM-DD-HHMM-short-description/
  spec.json
  document.docx
```

The `.docx` files are gitignored — only this README is tracked.

## Try it

```
/toolkit.word.create a one-page overview document of our project goals
```
