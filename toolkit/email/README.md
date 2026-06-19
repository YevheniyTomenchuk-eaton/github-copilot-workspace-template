---
title: "Email"
parent: "Toolkit"
---

# 📧 Email

Generate a polished, on-brand email draft as an `.eml` file. Double-click the result and it opens in Outlook as an editable draft with a **Send** button — brand header band, clean typography, and a styled signature divider already in place.

## How it works

This example needs **no script** — the prompt fills an HTML template directly:

- **Prompt:** `/toolkit.email.create` — gathers recipients, subject, and message, looks up your git identity as the sender, and writes the `.eml`.
- **Agent:** [`toolkit`](../../.github/agents/toolkit.agent.md) — the Office Document Producer that runs the job.
- **Skill:** [`office-documents`](../../.github/skills/office-documents/SKILL.md) — the brand system and the email tone rules.
- **Template:** `.github/templates/toolkit/email/toolkit.email.template.eml` — the branded `.eml` skeleton.
- **Instruction:** `.github/instructions/toolkit/email/toolkit.email.instructions.md` — headers, format, and naming rules.

## Output

Each email lands in its own timestamped folder here:

```text
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

The generated `.eml` files are gitignored — only this README is tracked.

## Try it

Open Copilot Chat and run:

```text
/toolkit.email.create draft a note to my team summarising this week's progress
```
