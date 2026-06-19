---
description: "Create an Outlook-ready email draft as an .eml file. Use when the user says 'draft an email', 'write an email', or '/toolkit.email.create'."
agent: "agent"
---

# Create Email Draft

Generate an `.eml` email draft that opens in Outlook as an editable draft. Follow the rules in [`toolkit.email.instructions.md`](../../../instructions/toolkit/email/toolkit.email.instructions.md).

## 1. Gather the details

Ask the user for anything missing:

- **Recipients** (To, and optional CC) — display name and email address.
- **Subject** — or propose one from the topic.
- **Message** — the point of the email, in the user's own words.

## 2. Determine the sender

Run both commands and use the result as the `From` identity:

```
git config user.name
git config user.email
```

Never hardcode a sender — the person running this prompt is always the sender.

## 3. Build the draft

1. Copy [`toolkit.email.template.eml`](../../../templates/toolkit/email/toolkit.email.template.eml) as the starting point.
2. Fill in `From`, `To`, optional `CC`, `Subject`, and `Date` (RFC 2822, sender's local timezone).
3. Write the body as the HTML inside `<body>` — short paragraphs, purpose first, first-name signature.
4. Keep `X-Unsent: 1` and the `Content-Type` header exactly as in the template.

## 4. Save the output

Write the file to a timestamped folder:

```
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

Use the current date and time for the prefix and a kebab-case description. Confirm the path to the user and remind them they can double-click it to open the draft in Outlook.
