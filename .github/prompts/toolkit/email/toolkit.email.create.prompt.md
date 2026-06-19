---
description: "Create an Outlook-ready email draft as an .eml file. Use when the user says 'draft an email', 'write an email', or '/toolkit.email.create'."
agent: "toolkit"
---

# Create Email Draft

Turn a message into a polished, on-brand `.eml` draft that opens in Outlook with a **Send** button. You fill the HTML template directly — no script needed.

## 1. Load the rules

Read these before writing anything:

1. [`office-documents`](../../../skills/office-documents/SKILL.md) skill — the brand system and the email rules (section 5).
2. [`toolkit.email.instructions.md`](../../../instructions/toolkit/email/toolkit.email.instructions.md) — headers, format, and naming.
3. [`toolkit.instructions.md`](../../../instructions/toolkit/toolkit.instructions.md) — general writing style.

## 2. Gather the details

Ask for anything missing:

- **Recipients** (To, optional CC) — display name and email address.
- **Subject** — or propose one from the topic.
- **Message** — the point of the email, in the user's words.

## 3. Determine the sender

Run both commands and use the result as the `From` identity. Never hardcode a sender — the person running this prompt is always the sender.

```
git config user.name
git config user.email
```

## 4. Build the draft

1. Copy [`toolkit.email.template.eml`](../../../templates/toolkit/email/toolkit.email.template.eml) as the starting point.
2. Fill `From`, `To`, optional `CC`, `Subject`, and `Date` (RFC 2822, sender's local timezone).
3. Replace only the body copy — keep the brand header band, the typography, and the signature divider from the template.
4. Keep `X-Unsent: 1` and the `Content-Type` header exactly as in the template.
5. First sentence states the purpose. Short paragraphs. First-name signature.

## 5. Save the output

Write the file to a timestamped folder:

```
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

Confirm the path and remind the user they can double-click it to open the draft in Outlook.

## Example

```
/toolkit.email.create draft a note to my team summarising this week's progress
```
