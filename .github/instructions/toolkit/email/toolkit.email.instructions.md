---
applyTo: "toolkit/email/**"
---

# Email Instructions

Create email drafts in `.eml` format that open in Outlook as ready-to-send drafts.

## Template

Use the template at `.github/templates/toolkit/email/toolkit.email.template.eml`. The `.eml` format is both the template and the output format.

## Rules

- **Format:** Always `.eml` with `X-Unsent: 1` header.
- **Content-Type:** `text/html; charset=utf-8`.
- **Font:** Calibri 11pt (Outlook default). Set via inline CSS on `<body>`.
- **From:** Always run `git config user.name` and `git config user.email` to get the current user, and use that identity as the sender. Never assume or hardcode a sender — the person running the prompt is always the sender.
- **To/CC:** Use full format: `Display Name <email@example.com>`. Ask the user for recipients if not given. If a recipient is documented under [`organization/people/`](../../../../organization/people/README.md), pull their display name and address from their person page instead of guessing.
- **Subject:** Short and specific. Include the topic. No filler like "Regarding" or "About".
- **Tone:** Professional but not stiff. Simple sentences. Direct.
- **Length:** As short as possible. Get to the point in the first sentence.
- **Signature:** First name only. No title or phone unless requested.

## Output Structure

Each email gets its own folder:

```
toolkit/email/YY-MM-DD-HHMM-short-description/email.eml
```

Folder name: kebab-case, prefixed with a `YY-MM-DD-HHMM` timestamp. Main file is `email.eml`. Name additional files descriptively if needed.

## .eml Format Reference

```
From: Sender Name <sender@example.com>
To: Recipient Name <recipient@example.com>
CC: Another Person <another@example.com>
Subject: Subject line here
Date: Mon, 09 Mar 2026 10:00:00 +0100
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8
X-Unsent: 1

<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Calibri, Arial, sans-serif; font-size: 11pt;">

<p>Opening line.</p>

<p>Body content.</p>

<p>Best regards,<br>
FirstName</p>

</body>
</html>
```

## Key Header Notes

- `X-Unsent: 1` makes Outlook open the file as an editable draft with a Send button.
- `Date:` uses RFC 2822 format with the sender's local timezone offset.
- Multiple recipients: separate with `, ` in the To/CC fields.

## Email Style

- First sentence states the purpose. No "I hope this email finds you well."
- Use `<ul>` / `<ol>` for lists in the HTML body.
- Use `<table>` for tabular data.
- Keep paragraphs to 2–3 sentences max.
- End with a clear ask or next step if one exists.

## Subject Examples

Good:

- "Sprint 24 review summary"
- "Budget figures needed for Q3 report"
- "Onboarding schedule for new hires"

Bad:

- "Regarding the review" (vague)
- "Quick question" (uninformative)
- "FYI" (says nothing)
