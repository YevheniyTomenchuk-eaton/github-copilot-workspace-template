#!/usr/bin/env python3
"""Build a PowerPoint .pptx deck from a JSON content spec.

Usage:
    python build-presentation.py <spec.json> <output.pptx>

The spec is a JSON object:
    {
      "title": "Deck title",
      "subtitle": "Optional subtitle",
      "slides": [
        {"title": "Slide title", "bullets": ["point one", "point two"]}
      ]
    }

Emits machine-readable KEY=value lines on success:
    OUTPUT=<absolute path to the .pptx>
    SLIDES=<number of content slides>

Requires: python-pptx  (pip install python-pptx)
"""

import json
import os
import sys


def build(spec_path: str, output_path: str) -> None:
    try:
        from pptx import Presentation
        from pptx.util import Pt
    except ImportError:
        print("ERROR=python-pptx not installed. Run: pip install python-pptx")
        sys.exit(1)

    with open(spec_path, encoding="utf-8") as spec_file:
        spec = json.load(spec_file)

    presentation = Presentation()

    title_layout = presentation.slide_layouts[0]
    title_slide = presentation.slides.add_slide(title_layout)
    title_slide.shapes.title.text = spec.get("title", "Untitled")
    if spec.get("subtitle"):
        title_slide.placeholders[1].text = spec["subtitle"]

    content_layout = presentation.slide_layouts[1]
    slides = spec.get("slides", [])
    for slide_spec in slides:
        slide = presentation.slides.add_slide(content_layout)
        slide.shapes.title.text = slide_spec.get("title", "")
        body = slide.placeholders[1].text_frame
        body.clear()
        bullets = slide_spec.get("bullets", [])
        for index, bullet in enumerate(bullets):
            paragraph = body.paragraphs[0] if index == 0 else body.add_paragraph()
            paragraph.text = str(bullet)
            paragraph.font.size = Pt(18)

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    presentation.save(output_path)

    print(f"OUTPUT={output_path}")
    print(f"SLIDES={len(slides)}")


def main() -> None:
    if len(sys.argv) != 3:
        print("ERROR=usage: python build-presentation.py <spec.json> <output.pptx>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
