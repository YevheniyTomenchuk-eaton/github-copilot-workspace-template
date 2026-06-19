---
applyTo: "toolkit/word/**"
---

# Word Instructions

Generate Word `.docx` documents by writing a JSON content spec and calling the build script. Never construct the binary `.docx` by hand.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/word/toolkit.word.template.json`
- **Script (generator):** `.github/scripts/toolkit/word/build-document.py`

## Spec format

The spec is a JSON object with a `title` and a `sections` array. Each section has a `heading` and a `paragraphs` array:

```json
{
  "title": "Document title",
  "sections": [
    {"heading": "Overview", "paragraphs": ["First paragraph.", "Second paragraph."]}
  ]
}
```

## Rules

- **Deterministic generation belongs in the script.** The prompt turns the user's request into a valid spec and calls the script — never hand-author `.docx` contents.
- **Use real prose.** Paragraphs are full sentences, not bullet fragments.
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

The script prints `OUTPUT=<path>` and `SECTIONS=<n>` on success. Parse those lines to confirm the result, then report the output path to the user.
