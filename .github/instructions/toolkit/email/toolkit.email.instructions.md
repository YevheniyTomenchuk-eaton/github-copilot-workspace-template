---
applyTo: "toolkit/email/**"
---

# Email Instructions

Create email drafts in `.eml` format that open in Outlook as ready-to-send drafts. This category needs no script — fill the HTML template directly.

## Design system & tone

The brand palette and the email tone rules live in the [`office-documents`](../../../skills/office-documents/SKILL.md) skill, section 5. Read it before drafting.

## Template

Use `.github/templates/toolkit/email/toolkit.email.template.eml`. It carries a brand header band, clean typography, and a styled signature divider. Keep that structure — only swap the copy.

## Rules

- **Format:** Always `.eml` with the `X-Unsent: 1` header so Outlook opens it as an editable draft.
- **Content-Type:** `text/html; charset=utf-8`.
- **From:** Always run `git config user.name` and `git config user.email` and use that identity. Never hardcode a sender — the person running the prompt is always the sender.
- **To/CC:** Full format `Display Name <email@example.com>`. Ask for recipients if not given.
- **Subject:** Short and specific. The topic, not "Regarding" or "Quick question".
- **Tone:** Professional, direct, simple sentences.
- **Length:** As short as possible. Purpose in the first sentence.
- **Signature:** First name only, above the accent divider in the template.

## Output Structure

Each email gets its own folder:

```
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

Folder name: kebab-case, prefixed with a `YY-MM-DD-HHMM` timestamp. Main file is `email.eml`.

## Subject Examples

Good: "Sprint 24 review summary" · "Budget figures needed for Q3 report" · "Onboarding schedule for new hires"

Bad: "Regarding the review" (vague) · "Quick question" (uninformative) · "FYI" (says nothing)
