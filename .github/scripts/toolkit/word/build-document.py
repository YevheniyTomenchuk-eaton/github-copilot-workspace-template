#!/usr/bin/env python3
"""Build a Word .docx document from a JSON content spec.

Usage:
    python build-document.py <spec.json> <output.docx>

The spec is a JSON object:
    {
      "title": "Document title",
      "sections": [
        {
          "heading": "Section heading",
          "paragraphs": ["First paragraph.", "Second paragraph."]
        }
      ]
    }

Emits machine-readable KEY=value lines on success:
    OUTPUT=<absolute path to the .docx>
    SECTIONS=<number of sections>

Requires: python-docx  (pip install python-docx)
"""

import json
import os
import sys


def build(spec_path: str, output_path: str) -> None:
    try:
        from docx import Document
    except ImportError:
        print("ERROR=python-docx not installed. Run: pip install python-docx")
        sys.exit(1)

    with open(spec_path, encoding="utf-8") as spec_file:
        spec = json.load(spec_file)

    document = Document()

    if spec.get("title"):
        document.add_heading(spec["title"], level=0)

    sections = spec.get("sections", [])
    for section in sections:
        if section.get("heading"):
            document.add_heading(section["heading"], level=1)
        for paragraph in section.get("paragraphs", []):
            document.add_paragraph(str(paragraph))

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    document.save(output_path)

    print(f"OUTPUT={output_path}")
    print(f"SECTIONS={len(sections)}")


def main() -> None:
    if len(sys.argv) != 3:
        print("ERROR=usage: python build-document.py <spec.json> <output.docx>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
