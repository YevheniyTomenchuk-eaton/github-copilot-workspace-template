---
applyTo: "toolkit/word/**"
---

# Word Instructions

Generate Word `.docx` documents by writing a JSON content spec and calling the build script. Never construct the binary `.docx` by hand.

## Design system & spec schema

The brand palette and the **full spec schema** (cover metadata, section `lead`, `callout`, `bullets`, `table`) live in the [`office-documents`](../../../skills/office-documents/SKILL.md) skill, section 4. Read it before writing a spec.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/word/toolkit.word.template.json`
- **Script (generator):** `.github/scripts/toolkit/word/build-document.py`

## Rules

- **Deterministic styling belongs in the script.** The prompt turns the request into a valid spec — never hand-author `.docx` contents.
- **Use real prose.** Paragraphs are full sentences, not bullet fragments.
- **Each section needs a `heading`.** Add `lead`, `paragraphs`, `callout`, `bullets`, or `table` only where they help.
- **Validate the spec is JSON** before calling the script.
- **Requires** `python-docx` (`pip install python-docx`).

## Output Structure

Each document gets its own timestamped folder:

```
toolkit/word/YY-MM-DD-HHMM-short-description/
  spec.json
  document.docx
```

The `.docx` files are gitignored — only the README is tracked.

## Running the script

```
python .github/scripts/toolkit/word/build-document.py <spec.json> <output.docx>
```

The script prints `OUTPUT=<path>` and `SECTIONS=<n>` on success. Parse those lines and report the output path.
