---
description: "Create an on-brand PowerPoint .pptx deck from a content spec. Use when the user says 'make a presentation', 'build a slide deck', or '/toolkit.presentation.create'."
agent: "toolkit"
---

# Create Presentation

Turn a topic into an on-brand PowerPoint deck. You write a JSON spec; the build script renders the branded title slide, section dividers, content layouts, and footers.

## 1. Load the rules

Read these before writing anything:

1. [`office-documents`](../../../skills/office-documents/SKILL.md) skill — the brand system and the full presentation spec schema (section 2).
2. [`toolkit.presentation.instructions.md`](../../../instructions/toolkit/presentation/toolkit.presentation.instructions.md) — output layout and naming.
3. [`toolkit.instructions.md`](../../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Gather the content

Ask only for what changes the deck: the topic, the audience, and the one message they should leave with. Decide a sensible flow — open with a `section` divider, one idea per content slide, 3–6 short bullets each. Use `two-column` for comparisons and a `quote` slide for a memorable line.

## 3. Write the spec

1. Copy [`toolkit.presentation.template.json`](../../../templates/toolkit/presentation/toolkit.presentation.template.json) as the starting point.
2. Fill `title`, `subtitle`, `author`, `footer`, and the `slides` array. Give every slide a `layout` (`bullets`, `section`, `two-column`, or `quote`).
3. Use specific, real content — real numbers and names, never "Point one".
4. Save to a timestamped folder: `toolkit/presentation/YY-MM-DD-HHMM-short-description/spec.json`.

## 4. Build the deck

```
python .github/scripts/toolkit/presentation/build-presentation.py toolkit/presentation/YY-MM-DD-HHMM-short-description/spec.json toolkit/presentation/YY-MM-DD-HHMM-short-description/presentation.pptx
```

If the script prints `ERROR=python-pptx not installed`, tell the user to run `pip install python-pptx` and retry.

## 5. Confirm

Read the `OUTPUT=` and `SLIDES=` lines and report the path and slide count.

## Example

```
/toolkit.presentation.create a 6-slide Q3 review for the leadership team — three wins, plan vs. actual, and next quarter's focus
```
