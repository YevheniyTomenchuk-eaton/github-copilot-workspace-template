---
title: "Demo Prompts"
parent: "Workspace"
---

# 🎬 Demo Prompts

A small set of **presenter prompts** built to showcase GitHub Copilot Chat controls live, during a walkthrough of the [Using GitHub Copilot](../using-copilot/README.md) guide. Each one deliberately triggers a specific chat behaviour so the audience can watch it happen on screen.

They are designed to leave **no lasting changes** — every prompt is idle, self-cleaning, or restores any setting it touches. Restoration is best-effort: `workspace.demo.permission-levels` temporarily changes the `chat.tools.global.autoApprove` user setting and only restores it at the end, so cancelling that prompt early can leave the setting changed and require a manual revert (the prompt notes the original value for this reason). The `workspace.demo.hooks-tour` demo installs a **temporary** hook and removes it at the end, so no hook ships in the repo to disturb normal work. Invoke each with `/<name>` and follow the on-screen steps.

## Available demos

| Prompt | Showcases | What it does |
|--------|-----------|--------------|
| `workspace.demo.clarifying-questions` | The interactive question control | Receives a deliberately vague request and stops to ask selectable clarifying questions before doing anything. |
| `workspace.demo.permission-levels` | Default approvals vs. Bypass permissions vs. Autopilot | Triggers tool actions that require approval (web fetch, terminal, out-of-workspace file edit) and asks a question to prove questions always pause — even in Autopilot. Reads, disables, and restores `chat.tools.global.autoApprove` automatically. |
| `workspace.demo.steering-and-queueing` | Steering, queued messages, and Stop | Runs a non-breaking timed countdown loop in the foreground so the presenter can steer, queue messages, and cancel while a run is active. |
| `workspace.demo.hooks-tour` | Every hook event in one run | Installs one temporary hook that maps all events to a single guide script, then triggers each event live — blocks an action, reacts after a tool and **chains a follow-up step on its own**, briefs and collects a subagent, captures an error, and resumes once before finishing — then guides a fresh chat for the session-start/end events. Removes the hook and markers at the end. |

## Presenter notes

- Run these in a clean chat session so the audience sees each behaviour from a known starting point.
- The `permission-levels` demo restores `chat.tools.global.autoApprove` to its original value as its final step — confirm the summary says so before moving on.
- The `steering-and-queueing` loop changes nothing on disk and is safe to cancel at any moment.
- The `hooks-tour` demo is the **exhaustive** one — it fires every lifecycle event in a single run, including a **block** (PreToolUse) and a real **chain** where a background task finishes and the PostToolUse hook hands the agent a follow-up step unprompted. It creates a temporary hook file (`.github/hooks/workspace.demo.hooks-tour.json`) and a `demo-hooks-tour` marker folder in TEMP, both deleted in its final step; if you cancel early, run `powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/install-tour-hook.ps1 -Remove` to delete them. Its guide script is inert unless that marker folder exists, so it never disturbs real work. `SessionStart`/`SessionEnd` are shown via a quick guided new-chat step, and `PreCompact` is explained rather than force-triggered (forcing context trimming would waste tokens).
