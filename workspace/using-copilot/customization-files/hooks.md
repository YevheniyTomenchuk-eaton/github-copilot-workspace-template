---
title: "Hooks — automation that fires on an event"
parent: "Customization files"
grand_parent: "Using GitHub Copilot"
nav_order: 5
---

# 4️⃣ Hooks — automation that fires on an event

| ← Previous | Next → |
|:---|---:|
| [Agents](agents.md) | [Templates](templates.md) |

---

A **hook** is an automation that runs **by itself when something happens** — not when you ask. An [instruction](instructions.md) is an ambient *rule* the AI reads; a hook is an ambient *action* tied to a moment: *before* the agent uses a tool, *after* a file is edited, *when* a session starts. The key idea is the **event** it listens for.

The difference that matters: an instruction only *guides*, but a hook runs **your own code** and can **enforce** an outcome — a `PreToolUse` hook can even **stop** an action before it runs. That makes hooks perfect for **guardrails**, **auto-formatting**, and **audit trails** — things you want guaranteed, not just requested.

> 🎬 **See every event live:** run the [`/workspace-demo-hooks-tour`](../../demo/README.md) demo. It installs one temporary hook file that maps all events to the same guide script, then triggers them one by one — a block, an auto-action, a real chain where a hook hands the agent a follow-up step unprompted, a subagent, an error, a continue — so you can watch each one fire, then removes the hook so nothing is left behind.

---

## 🗂️ What a hook looks like

Hooks are small **JSON** files in `.github/hooks/`. Each one maps an **event** to a command — almost always a **[script](scripts.md)**, so the logic stays in one place and the hook only *names* it:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/hook-tour.ps1",
        "windows": "powershell -ExecutionPolicy Bypass -File .github\\scripts\\workspace\\demo\\hook-tour.ps1"
      }
    ]
  }
}
```

---

## ⏱️ The lifecycle events

VS Code can fire a hook at each of these moments. You only wire up the ones you need.

| Event | Fires… | Typical use |
|-------|--------|-------------|
| **`SessionStart`** | a new chat session begins | add project context (branch, version) |
| **`UserPromptSubmit`** | you send a prompt | audit the request, inject context |
| **`PreToolUse`** | **before** the agent uses any tool | **block** a dangerous action, require approval |
| **`PostToolUse`** | **after** a tool finishes | auto-format, lint, or chain the next step |
| **`PreCompact`** | before the chat history is trimmed to fit | save important context first |
| **`SubagentStart`** | a subagent is spawned | brief or set up the subagent |
| **`SubagentStop`** | a subagent finishes | gather its results, clean up |
| **`Stop`** | the agent finishes its turn | run the tests, send a notification |

> 🔎 Newer VS Code builds add two more — **`SessionEnd`** (the session closes) and **`ErrorOccurred`** (something went wrong mid-session). The `/hooks` picker always shows the exact list your version supports.

---

## 🔌 How a hook talks to the agent

When the event fires, VS Code pipes a small JSON payload to your command on **stdin**, and reads JSON your command prints to **stdout** to decide what happens next:

- **Block an action** — a `PreToolUse` hook returns `permissionDecision: "deny"` (or `"ask"`) and the tool never runs.
- **Inject context** — `SessionStart`/`PostToolUse` hooks return `additionalContext`, quietly handing the agent more information.
- **Keep going** — a `Stop` hook can return `decision: "block"` with a reason, telling the agent to continue (e.g. "run the tests first").
- **Exit code `2`** is the simplest block of all — no JSON needed.

> ⚠️ A hook runs a shell command with the same permissions as VS Code. Keep any committed hook **inert by default** (the tour demo ships no committed hook — it installs a temporary one only while the demo runs, and its script stays inert unless a marker folder exists), and never hardcode secrets.

---

## 🛠️ How to create one — you don't hand-write JSON

| Way | How |
|-----|-----|
| **Describe it** | Type **`/create-hook`** and say what you want ("run the linter after every edit"). The AI generates the file. |
| **Pick it** | Run **`/hooks`** (or Command Palette → *Chat: Configure Hooks*). Choose the lifecycle event, then add or edit a hook; VS Code creates the file and drops your cursor on the command. |

Either way, the command it runs should be a **[script](scripts.md)** — never inlined logic.

---

## 📛 Naming & placement in this repo

The `/hooks` UI writes hook files **flat** into `.github/hooks/` — that folder is registered by default, so a flat file loads with **zero extra config**. We keep that flat placement but give each file a **mirrored dot-name** so it still says what it supports:

```text
.github/hooks/workspace.demo.hooks-tour.json    ← encodes workspace/demo/, sits flat
```

> 🧩 **Why flat?** VS Code's hook loader reads only the `*.json` files **directly in** a registered folder — it does **not** recurse into subfolders. Flat placement means every hook loads from the default `.github/hooks` location automatically; a nested subfolder would need its own `chat.hookFilesLocations` entry in `.vscode/settings.json`.

VS Code also accepts two JSON shapes: its native **PascalCase** keys (`PreToolUse`) and the Copilot-CLI **camelCase** form (`preToolUse`, with an optional `"version": 1` and a `powershell`/`bash` property). Both work; the `/hooks` UI may emit either.

---

| ← Previous | Next → |
|:---|---:|
| [Agents](agents.md) | [Templates](templates.md) |
