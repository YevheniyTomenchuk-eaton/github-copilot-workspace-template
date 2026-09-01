---
name: toolkit-word-create
description: "Create an on-brand Word .docx document from a content spec. Use when the user says 'write a report', 'draft a document', 'make a one-pager', or '/toolkit-word-create'."
---

# Create Document

Turn a topic into an on-brand Word document. You write a JSON spec; the build script renders the cover page, styled headings, lead lines, callout boxes, banded tables, and a page footer.

## 1. Load the rules

Read these before writing anything:

1. [`office-documents`](../office-documents/SKILL.md) skill — the brand system and the full Word spec schema (section 4).
2. [`toolkit.word.instructions.md`](../../instructions/toolkit/word/toolkit.word.instructions.md) — output layout and naming.
3. [`toolkit.instructions.md`](../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Gather the content

Ask only for what changes the document: the topic, the audience, and the recommendation or conclusion. Plan the sections — one topic each. Use a `lead` line to open a section, a `callout` for the one thing readers must remember, and a `table` for structured comparisons.

## 3. Write the spec

1. Copy [`toolkit.word.template.json`](../../templates/toolkit/word/toolkit.word.template.json) as the starting point.
2. Fill `title`, `subtitle`, `author`, `date`, and the `sections` array. Each section needs a `heading`; add `lead`, `paragraphs`, `callout`, `bullets`, or `table` as needed.
3. Write real prose — full sentences, not bullet fragments.
4. Save to a timestamped folder: `toolkit/word/YY-MM-DD-HHMM-short-description/spec.json`.

## 4. Build the document

```
python .github/scripts/toolkit/word/build-document.py toolkit/word/YY-MM-DD-HHMM-short-description/spec.json toolkit/word/YY-MM-DD-HHMM-short-description/document.docx
```

If the script prints `ERROR=python-docx not installed`, tell the user to run `pip install python-docx` and retry.

## 5. Confirm

Read the `OUTPUT=` and `SECTIONS=` lines and report the path and section count.

## Example

```
/toolkit-word-create a one-page vendor evaluation report comparing three suppliers with a recommendation
```
