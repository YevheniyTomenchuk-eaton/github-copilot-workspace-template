---
title: "Presentation"
parent: "Toolkit"
---

# 📊 Presentation

Generate an on-brand PowerPoint deck, then upload it to SharePoint. The output is a 16:9 widescreen `.pptx` with a branded title slide, section dividers, content layouts, and slide-number footers.

## Skills

| Skill | What it does |
|-------|--------------|
| `/toolkit-presentation-create` | Turn a topic into a JSON spec and build the styled `.pptx` |
| `/toolkit-presentation-upload` | Upload the generated `.pptx` to a SharePoint folder you choose |

## Slide layouts

| Layout | Renders |
|--------|---------|
| `bullets` | Colored title bar, accent underline, optional kicker, accent bullet markers |
| `section` | Full-bleed divider slide to break the deck into parts |
| `two-column` | Two shaded panels — perfect for plan vs. actual or before/after |
| `quote` | A large pull quote with an accent bar and attribution |

## Sources

| What | Where |
|------|-------|
| Brand system + slide spec schema | [`office-documents`](../../.github/skills/office-documents/SKILL.md) |
| Spec template | `.github/templates/toolkit/presentation/toolkit.presentation.template.json` |
| Generator script | `.github/scripts/toolkit/presentation/build-presentation.py` |
| Upload script | [`sharepoint-upload`](../../.github/skills/sharepoint-upload/SKILL.md) |

## Outputs

| What | Where |
|------|-------|
| Per-run folder | `toolkit/presentation/YY-MM-DD-HHMM-short-description/` |
| Deck | `toolkit/presentation/YY-MM-DD-HHMM-short-description/presentation.pptx` |

All generated content under `toolkit/presentation/` is gitignored. Only this README is tracked. Run `pip install python-pptx` once before the first build.

## Folder layout

```text
toolkit/presentation/
└── YY-MM-DD-HHMM-short-description/
    ├── spec.json            # the spec the generator built from
    └── presentation.pptx    # the styled deck
```
