---
title: "Email"
parent: "Toolkit"
---

# 📧 Email

Generate an Outlook-ready email draft as an `.eml` file. Double-click the result and it opens in Outlook as an editable draft with a **Send** button.

## How it works

This example needs **no script** — the prompt fills a text template directly:

- **Prompt:** `/toolkit.email.create` — gathers the recipients, subject, and message, looks up your git identity as the sender, and writes the `.eml`.
- **Template:** `.github/templates/toolkit/email/toolkit.email.template.eml` — the `.eml` skeleton.
- **Instruction:** `.github/instructions/toolkit/email/toolkit.email.instructions.md` — formatting and naming rules.

## Output

Each email lands in its own timestamped folder here:

```
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

The generated `.eml` files are gitignored — only this README is tracked.

## Try it

Open Copilot Chat and run:

```
/toolkit.email.create draft a note to my team summarising this week's progress
```
