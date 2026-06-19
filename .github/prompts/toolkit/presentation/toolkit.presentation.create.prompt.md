---
description: "Create a PowerPoint .pptx deck from a content spec. Use when the user says 'make a presentation', 'build a slide deck', or '/toolkit.presentation.create'."
agent: "agent"
---

# Create Presentation

Generate a PowerPoint deck by writing a JSON spec and calling the build script. Follow the rules in [`toolkit.presentation.instructions.md`](../../../instructions/toolkit/presentation/toolkit.presentation.instructions.md).

## 1. Gather the content

Ask the user for the deck topic and the key points to cover. Decide a sensible slide breakdown — one idea per slide, 3–6 short bullets each.

## 2. Write the spec

1. Copy [`toolkit.presentation.template.json`](../../../templates/toolkit/presentation/toolkit.presentation.template.json) as the starting point.
2. Fill in `title`, optional `subtitle`, and the `slides` array.
3. Save it to a timestamped folder: `toolkit/presentation/YY-MM-DD-HHMM-short-description/spec.json`.

## 3. Build the deck

Run the generator:

```
python .github/scripts/toolkit/presentation/build-presentation.py toolkit/presentation/YY-MM-DD-HHMM-short-description/spec.json toolkit/presentation/YY-MM-DD-HHMM-short-description/presentation.pptx
```

If the script prints `ERROR=python-pptx not installed`, tell the user to run `pip install python-pptx` and retry.

## 4. Confirm

Read the `OUTPUT=` and `SLIDES=` lines from the script output. Report the output path and slide count to the user.
