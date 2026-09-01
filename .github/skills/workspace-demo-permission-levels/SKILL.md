---
name: workspace-demo-permission-levels
description: 'Trigger tool actions that require approval, to contrast the Default approvals, Bypass permissions, and Autopilot permission levels.'
---

# Permission Levels

This skill deliberately invokes actions that normally require **tool approval**,
so the presenter can show how the three **permission levels** differ:

| Permission level | Tool actions (fetch / terminal / file edit) | Asking the presenter a question |
|------------------|---------------------------------------------|----------------------------------|
| **Default approvals** | An **Allow** / **Allow once** prompt appears for each action — the presenter clicks it. | Always pauses for an answer. |
| **Bypass permissions** | No prompt — the action runs automatically. | Always pauses for an answer. |
| **Autopilot** | No prompt — the action runs automatically. | Always pauses for an answer. |

> **Key insight for the Autopilot segment:** permission levels only govern *tool
> approvals*. Directly **asking the presenter a question** is an interaction, not
> a tool approval, so it pauses for input in **every** mode — even Autopilot. That
> is the one thing Autopilot does **not** auto-advance, and it's worth calling out
> live.

## ⚠️ Required setup before the demo

A single user setting can silently auto-approve **everything** and defeat this
demo. This skill handles it automatically: **step 1 reads the current value of
`chat.tools.global.autoApprove`, remembers it, and sets it to `false`**, then the
**final step restores it to exactly the remembered value**.

```jsonc
// settings.json — must be false (or removed) to see Default-approval prompts
"chat.tools.global.autoApprove": false
```

When `chat.tools.global.autoApprove` is `true`, no terminal command, web fetch,
or file edit will ever prompt — regardless of the permission-level picker. The
actions below are also chosen to **not** match a typical
`chat.tools.terminal.autoApprove` allow-list or `chat.tools.urls.autoApprove`
domain list, so they surface the approval gate cleanly.

## What to do

1. **Disable the global auto-approve override (and remember the old value).**
   Read the user setting `chat.tools.global.autoApprove`, note its current value
   so it can be restored later, and set it to `false`. Use the
   `Preferences: Open User Settings (JSON)` command or edit the user
   `settings.json` directly. Confirm in chat what the previous value was (for
   example, `true`) before continuing.

   > ⚠️ **Safety:** before changing it, write the original value into the chat
   > (and ideally copy it somewhere) as a backup. **If you stop or cancel this
   > prompt before step 6 runs, the setting will be left as `false` — restore it
   > manually** by setting `chat.tools.global.autoApprove` back to the value you
   > noted here.

2. **Fetch a web page from a fresh domain.** Fetch this URL — a domain unlikely
   to be in any `chat.tools.urls.autoApprove` list, so it triggers the per-domain
   **Allow / Allow domain** dialog:

   `https://www.rfc-editor.org/rfc/rfc2324`

3. **Run a terminal command whose head is unlikely to be allow-listed.** Launch a
   URL in the default browser:

   ```powershell
   Start-Process "https://www.rfc-editor.org/rfc/rfc2324"
   ```

4. **Edit a file outside the workspace.** Create a throwaway file in the OS temp
   directory (outside the workspace edit gate), then delete it:

   - Create `$env:TEMP\vg-approval-demo.txt` with content `approval gate demo`.
   - Then remove it:

     ```powershell
     Remove-Item "$env:TEMP\vg-approval-demo.txt" -Force
     ```

5. **Ask the presenter a question (always pauses, even in Autopilot).** Using the
   interactive question control, ask one short multiple-choice question — for
   example: *"Which permission level are you demonstrating right now?"* with the
   options **Default approvals**, **Bypass permissions**, **Autopilot**. Wait for
   the answer before continuing. Do this step near the end, so that in Autopilot
   the audience sees every tool action fly by automatically and then the agent
   still stops here to ask — proving questions are never auto-answered.

6. **Restore the global auto-approve override.** Set
   `chat.tools.global.autoApprove` back to the exact value remembered in step 1
   (do not assume `true` — use whatever was actually there). This is the last
   thing the skill does, so the box is left exactly as it was found.

After all steps, reply with a short summary stating which steps ran, whether an
approval prompt appeared for each tool action, confirming that the question
paused for input regardless of the permission level, and confirming that
`chat.tools.global.autoApprove` was restored to its original value.

> All actions are safe and reversible. Their only purpose is to surface the
> approval gate — and the always-on question pause — so the presenter can contrast
> the three permission levels. The global setting is flipped off at the start and
> restored to its original value at the end.
