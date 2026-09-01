---
title: "Email"
parent: "Toolkit"
---

# 📧 Email

Generate an on-brand email draft as an `.eml` file. Double-click the result and it opens in Outlook as an editable draft with a **Send** button — brand header band, clean typography, and a styled signature divider already in place.

This category needs **no script** — the skill fills an HTML template directly, so there is nothing to upload to SharePoint.

## Skills

| Skill | What it does |
|-------|--------------|
| `/toolkit-email-create` | Gather recipients, subject, and message, look up your git identity as the sender, and write the `.eml` |

## Sources

| What | Where |
|------|-------|
| Brand system + email tone rules | [`office-documents`](../../.github/skills/office-documents/SKILL.md) |
| Email template | `.github/templates/toolkit/email/toolkit.email.template.eml` |

## Outputs

| What | Where |
|------|-------|
| Per-run folder | `toolkit/email/YY-MM-DD-HHMM-short-description/` |
| Email draft | `toolkit/email/YY-MM-DD-HHMM-short-description/email.eml` |

All generated `.eml` files are gitignored. Only this README is tracked.

## Folder layout

```text
toolkit/email/
└── YY-MM-DD-HHMM-short-description/
    └── email.eml        # the branded draft, opens in Outlook
```
