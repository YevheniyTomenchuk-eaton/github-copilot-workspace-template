---
applyTo: "toolkit/presentation/**"
---

# Presentation Instructions

Generate PowerPoint `.pptx` decks by writing a JSON content spec and calling the build script. Never construct the binary `.pptx` by hand.

## Pieces

- **Template (spec skeleton):** `.github/templates/toolkit/presentation/toolkit.presentation.template.json`
- **Script (generator):** `.github/scripts/toolkit/presentation/build-presentation.py`

## Spec format

The spec is a JSON object with a `title`, optional `subtitle`, and a `slides` array. Each slide has a `title` and a list of `bullets`:

```json
{
  "title": "Deck title",
  "subtitle": "Optional subtitle",
  "slides": [
    {"title": "Slide title", "bullets": ["point one", "point two"]}
  ]
}
```

## Rules

- **Deterministic generation belongs in the script.** The prompt's only job is to turn the user's request into a valid spec and call the script — never hand-author `.pptx` contents.
- **Content is concise.** Slide titles are short. Bullets are phrases, not paragraphs. Aim for 3–6 bullets per slide.
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

The script prints `OUTPUT=<path>` and `SLIDES=<n>` on success. Parse those lines to confirm the result, then report the output path to the user.
