---
applyTo: ".github/hooks/**"
---

# Authoring Hook Files — AI Instructions

Rules for creating and editing **agent hook** definition files under `.github/hooks/`. The shared
naming, encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
hook-specific delta. The VS Code [Agent hooks](https://code.visualstudio.com/docs/agent-customization/hooks)
documentation is the authority on the hook format and lifecycle events; read it when in doubt.

## What a Hook Is

A hook is a JSON file that maps a VS Code agent **lifecycle event** to one or more shell commands.
VS Code runs the command at that point in the session, pipes the event payload to the command on
**stdin**, and reads JSON the command prints to **stdout** to influence the agent (allow/deny a tool,
inject context, block stopping, …). The documented events are `SessionStart`, `UserPromptSubmit`,
`PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, and `Stop`; newer VS Code
builds also expose `SessionEnd` and `ErrorOccurred` in the `/hooks` picker. Event keys may be written
in VS Code's native PascalCase (`PreToolUse`) **or** the Copilot CLI lowerCamelCase form (`preToolUse`,
`sessionEnd`, `errorOccurred`), which VS Code converts to PascalCase on load. The validator accepts
both casings — consult the linked VS Code docs for the set your build supports.

## File Shape

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .github/scripts/<domain>/<name>.ps1",
        "windows": "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .github\\scripts\\<domain>\\<name>.ps1"
      }
    ]
  }
}
```

- The top-level **`hooks`** object is required; its keys must be valid event names (above).
- Each command entry needs `type: "command"` and at least one command property. Provide a
  `windows` override when the cross-platform `command` path uses POSIX separators.
- Command paths are **relative to the repository root**, not to the hook file — keep them
  root-relative regardless of where the hook file lives.
- The `/hooks` UI may emit an alternative **Copilot CLI** shape for some events: an optional
  top-level `"version": 1` field, **camelCase** event keys, and a `powershell` / `bash` command
  property (VS Code maps `powershell` → `windows` and `bash` → `osx`/`linux`). Both shapes are valid;
  prefer the native PascalCase + `command`/`windows` form shown above when authoring by hand.

## Keep Hooks Declarative — Never Inline Logic

A hook entry only names the command to run. Per the **Script it or template it** Universal Rule, the
thing a hook *runs* is a **script** under `.github/scripts/<domain>/`, never an inlined snippet. Do
not embed multi-line PowerShell/bash inside the `command` string — extract it to a script and point
the hook at that script. See [`.github/scripts/github/README.md`](../../../scripts/github/README.md)
for the script pattern.

## Mirroring & Naming

A hook's **filename** mirrors the project folder of the thing it supports — but the file itself lives
**flat** in `.github/hooks/`, not in a mirrored subfolder. This keeps the mirrored dot-name while
staying in the zero-config default location the hook loader always reads.

- A hook backing a demo under `workspace/demo/` is named `workspace.demo.hooks-tour.json` and lives
  directly at `.github/hooks/workspace.demo.hooks-tour.json`. The dot-path encodes the mirrored
  directory; the `.json` file sits flat. It pairs with the `/workspace-demo-hooks-tour` skill. The
  leading-dot, kebab-case, and no-consecutive-duplicate-segment rules from
  `copilot-instructions.md` apply.
- **Prefer this flat dot-name layout over mirrored subfolders.** VS Code's hook loader reads only the
  `*.json` files **directly in** a registered folder (no `**` recursion), so a mirrored subfolder
  would need its own `chat.hookFilesLocations` entry — extra friction for no gain. The flat
  `.github/hooks` folder is registered by default, so a flat dot-named hook loads with zero config.
- A bare top-level hook (`.github/hooks/<name>.json`) is also fine for ad-hoc, repo-wide automation
  that belongs to no single project folder.

## Registration — Hooks Do NOT Auto-Discover Subfolders

This is the one place hooks differ from instructions. VS Code's instruction loader accepts `**`
globs and recurses; the **hook loader does not**. For a folder entry, VS Code
loads only the `*.json` files **directly in that folder** (single level). The default `.github/hooks`
entry in `chat.hookFilesLocations` covers every flat dot-named hook — which is why the flat layout
above is preferred and needs **no** extra registration. Only add another entry to
[`.vscode/settings.json`](../../../../.vscode/settings.json) if you deliberately place a hook in a
subfolder:

```json
"chat.hookFilesLocations": {
  ".github/hooks": true
}
```

Forgetting to register a subfolder means VS Code never loads the hook — another reason to keep hooks
flat.

## Safety

A hook executes a shell command with the same permissions as VS Code. Keep committed hooks
**inert by default** — the demo chaining hook only reacts to a temporary marker file, so it never
disturbs normal work. Never hardcode secrets in a hook or its script; validate any stdin payload
before acting on it.

## Encoding

UTF-8 without BOM, CRLF line endings — same as all repository files.
