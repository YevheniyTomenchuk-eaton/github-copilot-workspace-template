---
name: office-documents
description: "Design and generate polished, on-brand Office documents — PowerPoint decks, Excel workbooks, Word documents, and Outlook email drafts — from the toolkit/ examples. Holds the shared brand system (color palette, typography, layout rules) and the full JSON spec schema each generator script accepts. Use when: building or restyling a presentation, workbook, document, or email; deciding slide layouts, sheet formatting, document structure, or email tone; or extending a toolkit generator. DO NOT USE FOR: choosing which .github/ artifact to create (use github-conventions) or non-document tasks."
---

# Office Documents — Design System & Spec Reference

This skill turns rough requests ("make a deck about Q3", "build a budget sheet") into **polished, on-brand** Office files. It owns two things every toolkit document generator shares:

1. **The brand system** — one palette, one type scale, one set of layout rules. Apply it to every document so a deck, a workbook, a report, and an email all look like one suite.
2. **The spec schemas** — the exact JSON each generator script accepts. The prompt's only job is to turn the request into a valid spec; the script does the deterministic styling.

> **Golden rule:** never hand-build a `.pptx`, `.xlsx`, or `.docx`. Write a JSON spec, call the script. The wow factor lives in the script — your job is great *content* in a valid spec.

---

## 1. Brand system

One palette and type scale drive all four generators. The same hex values are duplicated as constants at the top of each build script (scripts must be self-contained). Change them in one script to rebrand that surface; change them everywhere for a full rebrand.

### Palette

| Role | Hex | Where it shows up |
|------|-----|-------------------|
| **Primary** | `#1F4E79` | Title bars, cover blocks, sheet banners, email header |
| **Accent** | `#00B3A4` | Underlines, rules, bullet markers, key numbers |
| **Ink** | `#1A2233` | Body text, headings |
| **Muted** | `#5B6B7F` | Subtitles, captions, footers |
| **Band** | `#EEF3F9` | Alternating table/row banding |
| **Rule** | `#D5DEEA` | Hairline borders, dividers |

Always pair dark backgrounds with white text. Never put Muted text on Primary.

### Typography

| Level | Font | Size | Weight |
|-------|------|------|--------|
| Display (cover / title slide) | Calibri Light | 40–54 pt | Light |
| Heading | Calibri | 22–32 pt | Bold |
| Body | Calibri | 11 pt (docs) / 18 pt (slides) | Regular |
| Caption / footer | Calibri | 9 pt (docs) / 11 pt (slides) | Regular |

Calibri is the safe default on every Windows + Office install. Don't pick exotic fonts — they fall back unpredictably.

### Layout rules

- **One idea per unit** — one message per slide, one topic per section, one subject per email.
- **Breathe.** Generous margins and white space read as "premium". Crowding reads as "draft".
- **Accent sparingly.** The accent color marks *one* thing per view — the underline, the key number, the call to action. If everything is accented, nothing is.
- **Left-align** body text and headings. Center only cover/title blocks.
- **Be specific.** Real names, real numbers, real dates. Placeholders kill the wow.

---

## 2. Presentation spec (`build-presentation.py`)

16:9 widescreen. The script renders a branded title slide, optional section dividers, and content slides with a colored title bar, accent underline, and a footer with the deck name and slide number.

```json
{
  "title": "Q3 Business Review",
  "subtitle": "Sales & Operations",
  "author": "Dana Ruiz",
  "footer": "Q3 Business Review",
  "slides": [
    {"layout": "section", "title": "Where we are"},
    {"layout": "bullets", "kicker": "Overview", "title": "Three wins this quarter",
     "bullets": ["Revenue up 18% QoQ", "Two enterprise logos signed", "Churn down to 3.1%"]},
    {"layout": "two-column", "title": "Plan vs. actual",
     "left": ["Target: $4.0M", "Hires: 6", "NPS: 40"],
     "right": ["Actual: $4.3M", "Hires: 5", "NPS: 47"]},
    {"layout": "quote", "quote": "Best onboarding we've ever had.",
     "attribution": "Pilot customer, May 2026"}
  ]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `title`, `subtitle`, `author` | `title` only | Render on the title slide. |
| `footer` | optional | Shown bottom-left on every content slide. Defaults to `title`. |
| `slides[]` | yes | Each needs a `layout`. |

**Layouts:** `bullets` (title + `kicker?` + 3–6 `bullets`), `section` (divider, `title` only), `two-column` (`title` + `left[]` + `right[]`), `quote` (`quote` + `attribution?`). Unknown layouts fall back to `bullets`.

Content rules: slide titles are short phrases; bullets are phrases, not paragraphs; 3–6 bullets per slide; one idea per slide.

---

## 3. Excel spec (`build-workbook.py`)

Each sheet renders a colored banner title, a frozen bold header row, banded data rows, auto-fit columns, an auto-filter, and an optional bold totals row. Per-column `formats` apply number/currency/percent/date styling.

```json
{
  "sheets": [
    {
      "name": "Pipeline",
      "title": "Q3 Sales Pipeline",
      "headers": ["Deal", "Owner", "Value", "Probability", "Close date"],
      "formats": ["text", "text", "currency", "percent", "date"],
      "rows": [
        ["Acme renewal", "Dana", 120000, 0.8, "2026-08-15"],
        ["Globex expansion", "Lee", 90000, 0.45, "2026-09-01"]
      ],
      "totals": ["Total", "", 210000, "", ""]
    }
  ]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | Tab name, ≤31 chars (script truncates). |
| `title` | optional | Merged banner row above the headers. |
| `headers` | optional | Bold, colored, frozen. |
| `formats` | optional | One token per column: `text`, `number`, `currency`, `percent`, `date`. Missing → `text`. |
| `rows` | yes | Every row matches the header length. |
| `totals` | optional | Bold row with a top border. |

Currency renders `$#,##0`; percent expects a fraction (`0.8` → `80%`); date expects `YYYY-MM-DD`.

---

## 4. Word spec (`build-document.py`)

Renders a cover page (colored title block, subtitle, author, date, accent rule), a styled body with brand-colored headings, an optional lead paragraph, callout boxes, bullet lists, banded tables, and a page footer with the document title and page number.

```json
{
  "title": "Vendor Evaluation Report",
  "subtitle": "Procurement — Confidential",
  "author": "Dana Ruiz",
  "date": "2026-06-19",
  "sections": [
    {
      "heading": "Summary",
      "lead": "Three vendors were assessed against cost, support, and security.",
      "paragraphs": ["Vendor B scored highest overall and is recommended."],
      "callout": "Recommendation: proceed with Vendor B, pending a security review.",
      "bullets": ["Cost: 30%", "Support: 30%", "Security: 40%"],
      "table": {
        "headers": ["Vendor", "Score", "Cost"],
        "rows": [["Vendor A", "78", "$$"], ["Vendor B", "91", "$$$"]]
      }
    }
  ]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `title` | yes | Cover title. |
| `subtitle`, `author`, `date` | optional | Cover metadata. |
| `sections[]` | yes | Each needs a `heading`. |
| `lead` | optional | Larger intro line under the heading. |
| `paragraphs[]` | optional | Body prose — full sentences. |
| `callout` | optional | Shaded accent box for the one thing readers must remember. |
| `bullets[]` | optional | Bulleted list. |
| `table` | optional | `headers[]` + `rows[][]`, shaded header + banded rows. |

Use real prose in paragraphs — full sentences, not bullet fragments.

---

## 5. Email (`.eml`, template-driven, no script)

Fill `.github/templates/toolkit/email/toolkit.email.template.eml`. The template carries a brand header band, clean typography, and a styled signature divider. Keep the `X-Unsent: 1` header so Outlook opens it as an editable draft.

Rules:

- **Sender** = the person running the prompt. Always read `git config user.name` / `git config user.email`; never hardcode.
- **Subject** is short and specific — the topic, no "Regarding" / "Quick question" filler.
- **First sentence states the purpose.** No "I hope this finds you well."
- **Keep the brand header band and signature divider** from the template; only swap the copy.
- Paragraphs are 2–3 sentences. Use `<ul>`/`<table>` for lists and data. Sign with the first name only.

---

## 6. Running the generators

```bash
# one-time install
pip install python-pptx openpyxl python-docx

python .github/scripts/toolkit/presentation/build-presentation.py <spec.json> <out.pptx>
python .github/scripts/toolkit/excel/build-workbook.py        <spec.json> <out.xlsx>
python .github/scripts/toolkit/word/build-document.py         <spec.json> <out.docx>
```

Each script prints machine-readable `KEY=value` lines (`OUTPUT=`, plus `SLIDES=` / `SHEETS=` / `ROWS=` / `SECTIONS=`). Parse those to confirm the result and report the path. If a script prints `ERROR=<lib> not installed`, tell the user the `pip install` line and retry.

Outputs land in `toolkit/<category>/YY-MM-DD-HHMM-short-description/`. Everything but each category README is gitignored — never suggest committing generated files.
