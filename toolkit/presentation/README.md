---
title: "Presentation"
parent: "Toolkit"
---

# 📊 Presentation

Generate a PowerPoint `.pptx` deck from a short content spec.

## How it works

This example shows the **prompt → script** pattern:

- **Prompt:** `/toolkit.presentation.create` — turns your topic and key points into a JSON spec.
- **Template:** `.github/templates/toolkit/presentation/toolkit.presentation.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/presentation/build-presentation.py` — reads the spec and builds the `.pptx` with [`python-pptx`](https://python-pptx.readthedocs.io/).
- **Instruction:** `.github/instructions/toolkit/presentation/toolkit.presentation.instructions.md` — keeps generation in the script and content concise.

## Requirements

```bash
pip install python-pptx
```

## Output

```
toolkit/presentation/YY-MM-DD-HHMM-short-description/
  spec.json
  presentation.pptx
```

The `.pptx` files are gitignored — only this README is tracked.

## Try it

```
/toolkit.presentation.create a 4-slide overview of our onboarding process
```
