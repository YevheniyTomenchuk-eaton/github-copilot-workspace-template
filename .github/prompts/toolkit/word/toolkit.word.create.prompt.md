---
description: "Create a Word .docx document from a content spec. Use when the user says 'write a document', 'make a Word file', or '/toolkit.word.create'."
agent: "agent"
---

# Create Document

Generate a Word document by writing a JSON spec and calling the build script. Follow the rules in [`toolkit.word.instructions.md`](../../../instructions/toolkit/word/toolkit.word.instructions.md).

## 1. Gather the content

Ask the user for the document topic and the sections it should contain. Draft the prose yourself from their input — full sentences, organized under clear headings.

## 2. Write the spec

1. Copy [`toolkit.word.template.json`](../../../templates/toolkit/word/toolkit.word.template.json) as the starting point.
2. Fill in `title` and the `sections` array.
3. Save it to a timestamped folder: `toolkit/word/YY-MM-DD-HHMM-short-description/spec.json`.

## 3. Build the document

Run the generator:

```
python .github/scripts/toolkit/word/build-document.py toolkit/word/YY-MM-DD-HHMM-short-description/spec.json toolkit/word/YY-MM-DD-HHMM-short-description/document.docx
```

If the script prints `ERROR=python-docx not installed`, tell the user to run `pip install python-docx` and retry.

## 4. Confirm

Read the `OUTPUT=` and `SECTIONS=` lines from the script output. Report the output path and section count to the user.
