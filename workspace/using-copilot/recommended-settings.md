---
title: "Recommended settings"
parent: "Using GitHub Copilot"
grand_parent: "Workspace"
nav_order: 10
---

# ⚙️ Recommended settings

| ← Previous | Next → |
|:---|---:|
| [Running and monitoring](running-and-monitoring.md) | [Tips and tricks](tips-and-tricks.md) |

---

VS Code has **two** layers of settings. It helps to know which is which.

## Two layers of settings

| Layer | Where it lives | Who sets it |
|-------|----------------|-------------|
| **Workspace settings** | `.vscode/settings.json` **inside this repo** | Already shipped. Everyone who opens the repo gets them automatically (instruction, skill, agent, and hook locations, etc.). **You do not touch these.** |
| **Personal settings** | Your **User** `settings.json` on **your machine** | **You** set these. They follow you across every project. The repo cannot set them for you. |

This page is about the **personal** layer — a few settings that make Copilot much nicer to use, set once per machine.

---

## How to add them

1. Open the **Command Palette** from the **View** menu.
2. Run **"Preferences: Open User Settings (JSON)"**.
3. Copy the settings below **inside** the `{ }` braces.
4. **Save**. Done.

> 📄 Ready-made snippet: **[personal-settings.jsonc](assets/personal-settings.jsonc)** — open it, copy, paste.
>
> 🙋 **What is it?** A complete, working set of Copilot-relevant User settings, trimmed to the lines that matter. Copy it as-is, or take the few lines you want and build your own on top.

---

## What to add (the essentials)

These few lines give you the **two biggest wins**: the agent finishes a whole task without stopping, and it stops nagging you for approval on every step.

```jsonc
{
  // The star setting: let the agent finish a whole task
  // without stopping to ask "keep going?".
  "chat.agent.maxRequests": 1000000000,

  // Stop the constant approval pop-ups — auto-approve every command,
  // file edit, and web request. The agent still asks YOU a real
  // clarifying question when it genuinely needs a decision.
  "chat.tools.global.autoApprove": true,

  // Fewer extra confirmation dialogs in the chat editor.
  "chat.editing.confirmEditRequestRemoval": false,
  "chat.editing.confirmEditRequestRetry": false,

  // Smart inline code suggestions while you type.
  "editor.inlineSuggest.enabled": true,
  "github.copilot.nextEditSuggestions.enabled": true
}
```

> ⚠️ `chat.tools.global.autoApprove` is powerful — turn it on once your work is in **Git** so any change can be undone. While you are still learning, leave it off (see the [safer alternative](#-prefer-approving-only-safe-things) below).

The full [personal-settings.jsonc](assets/personal-settings.jsonc) adds a few extra comforts the author uses — voice dictation and Git quality-of-life tweaks.

---

## What each setting means

| Setting | Why |
|---------|-----|
| `chat.agent.maxRequests` = `1000000000` | **The important one.** The agent never stops mid-task to ask permission to continue. A huge number = effectively unlimited steps. |
| `chat.tools.global.autoApprove` = `true` | **The other big one.** No more "Allow?" pop-ups — every tool runs automatically. Same as **Bypass** in the [Approvals](permissions-and-autopilot.md) menu, but permanent. |
| `chat.editing.confirmEditRequestRemoval` / `...Retry` = `false` | Removes two extra "are you sure?" dialogs in the chat editor. |
| `editor.inlineSuggest.enabled` | Shows grey ghost-text code you can accept with **Tab**. |
| `github.copilot.nextEditSuggestions.enabled` | Suggests the next edit as you type. |

> 💡 These are **personal preferences**, not repository rules. Set whatever feels right on your machine — the repo will not override them.

---

## 🛡️ Prefer approving only safe things

`chat.tools.global.autoApprove` approves **everything**. If that feels like too much while you are learning, leave it off and instead approve only **specific** safe terminal commands and trusted URLs. VS Code grows these lists for you each time you click **"Always allow"**, so they fill up naturally:

```jsonc
  "chat.tools.terminal.autoApprove": {
    "python": true,
    "dir": true,
    "mkdir": true,
    "Test-Path": true,
    "Get-Content": true
  },
  "chat.tools.urls.autoApprove": {
    "https://just-the-docs.com": true,
    "https://mermaid.js.org": true
  }
```

> ✅ This is the safe middle ground: fewer pop-ups for the commands you trust, while still being asked about anything new. See the full lists in [personal-settings.jsonc](assets/personal-settings.jsonc).

---

| ← Previous | Next → |
|:---|---:|
| [Running and monitoring](running-and-monitoring.md) | [Tips and tricks](tips-and-tricks.md) |
