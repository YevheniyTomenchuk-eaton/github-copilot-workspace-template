---
title: "Toolkit"
nav_order: 8
has_toc: false
---

# 🛠️ Toolkit

Worked examples that show the full customization pattern end to end. Each one is a small, self-contained demonstration of how a **prompt** drives a **script** and fills a **template**, governed by an **instruction** file — exactly the shape you reuse for your own automations.

These examples generate everyday Office documents. To run the document generators, install their Python packages once:

```bash
pip install python-pptx openpyxl python-docx
```

## Examples

| Example | What it generates | How it works |
|---------|-------------------|--------------|
| [Email](email/README.md) | An Outlook-ready `.eml` draft | A template the prompt fills in — no script needed |
| [Presentation](presentation/README.md) | A PowerPoint `.pptx` deck | A prompt writes a JSON spec, a Python script builds the file |
| [Excel](excel/README.md) | An Excel `.xlsx` workbook | A prompt writes a JSON spec, a Python script builds the file |
| [Word](word/README.md) | A Word `.docx` document | A prompt writes a JSON spec, a Python script builds the file |

## The pattern they share

Every example wires together the same five pieces, mirroring the repo under `.github/`:

- **Instruction** (`.github/instructions/toolkit/<name>/`) — rules that auto-apply when you work in `toolkit/<name>/`.
- **Prompt** (`.github/prompts/toolkit/<name>/`) — the `/` command you invoke to start the job.
- **Template** (`.github/templates/toolkit/<name>/`) — the skeleton the output is built from.
- **Script** (`.github/scripts/toolkit/<name>/`) — the deterministic generator the prompt calls.
- **Output** (`toolkit/<name>/`) — where the generated file lands (gitignored; only the README is tracked).

Copy any one of these folders as the starting point for your own toolkit category.
