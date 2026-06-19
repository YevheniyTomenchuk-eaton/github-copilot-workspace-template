---
title: "Presentation"
parent: "Toolkit"
---

# 📊 Presentation

Generate a polished, on-brand PowerPoint deck from a one-line request. The output is a 16:9 widescreen `.pptx` with a branded title slide, section dividers, content layouts, and slide-number footers.

## How it works

- **Prompt:** `/toolkit.presentation.create` — turns your topic into a JSON spec and runs the build script.
- **Agent:** [`toolkit`](../../.github/agents/toolkit.agent.md) — the Office Document Producer that runs the job.
- **Skill:** [`office-documents`](../../.github/skills/office-documents/SKILL.md) — the brand system and the full slide-spec schema.
- **Template:** `.github/templates/toolkit/presentation/toolkit.presentation.template.json` — the spec skeleton.
- **Script:** `.github/scripts/toolkit/presentation/build-presentation.py` — renders the styled deck.
- **Instruction:** `.github/instructions/toolkit/presentation/toolkit.presentation.instructions.md` — output and naming rules.

## Slide layouts

| Layout | Renders |
|--------|---------|
| `bullets` | Colored title bar, accent underline, optional kicker, accent bullet markers |
| `section` | Full-bleed divider slide to break the deck into parts |
| `two-column` | Two shaded panels — perfect for plan vs. actual or before/after |
| `quote` | A large pull quote with an accent bar and attribution |

## Output

Each deck lands in its own timestamped folder here:

```text
toolkit/presentation/YY-MM-DD-HHMM-short-description/
  spec.json
  presentation.pptx
```

The generated files are gitignored — only this README is tracked. Run `pip install python-pptx` once before the first build.

## Try it

Open Copilot Chat and run:

```text
/toolkit.presentation.create a 6-slide Q3 review for leadership — three wins, plan vs. actual, and next quarter's focus
```
