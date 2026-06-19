---
applyTo: "toolkit/presentation/**"
---

# Presentation Instructions

Generate PowerPoint `.pptx` decks by writing a JSON content spec and calling the build script. Never construct the binary `.pptx` by hand.

## Design system & spec schema

The brand palette, type scale, layout rules, and the **full spec schema** (layouts, fields, defaults) live in the [`office-documents`](../../../skills/office-documents/SKILL.md) skill, section 2. Read it before writing a spec.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/presentation/toolkit.presentation.template.json`
- **Script (generator):** `.github/scripts/toolkit/presentation/build-presentation.py`

## Rules

- **Deterministic styling belongs in the script.** The prompt's only job is to turn the request into a valid spec — never hand-author `.pptx` contents.
- **One idea per slide.** Short titles. Bullets are phrases, not paragraphs. 3–6 bullets per slide.
- **Every slide needs a `layout`** (`bullets`, `section`, `two-column`, `quote`). Unknown layouts fall back to `bullets`.
- **Validate the spec is JSON** before calling the script.
- **Requires** `python-pptx` (`pip install python-pptx`).

## Output Structure

Each deck gets its own timestamped folder:

```
toolkit/presentation/YY-MM-DD-HHMM-short-description/
  spec.json
  presentation.pptx
```

The `.pptx` files are gitignored — only the README is tracked.

## Running the script

```
python .github/scripts/toolkit/presentation/build-presentation.py <spec.json> <output.pptx>
```

The script prints `OUTPUT=<path>` and `SLIDES=<n>` on success. Parse those lines and report the output path.
