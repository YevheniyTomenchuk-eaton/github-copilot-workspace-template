# Toolkit Scripts

Deterministic generators for the [Toolkit](../../../toolkit/README.md) examples. Each prompt **calls** its script rather than embedding the logic. Every script reads a JSON spec and writes an Office document, emitting machine-readable `KEY=value` lines so the calling prompt can parse the result.

| Script | Generates | Spec input | Output keys |
|--------|-----------|------------|-------------|
| [presentation/build-presentation.py](presentation/build-presentation.py) | PowerPoint `.pptx` | `{title, subtitle, slides[]}` | `OUTPUT`, `SLIDES` |
| [excel/build-workbook.py](excel/build-workbook.py) | Excel `.xlsx` | `{sheets[]}` | `OUTPUT`, `SHEETS`, `ROWS` |
| [word/build-document.py](word/build-document.py) | Word `.docx` | `{title, sections[]}` | `OUTPUT`, `SECTIONS` |

## Usage

```
python <script> <spec.json> <output-file>
```

Each script prints `ERROR=...` and exits non-zero when its Python package is missing.

## Requirements

```bash
pip install python-pptx openpyxl python-docx
```

The email example has no script — its prompt fills a text template directly.
