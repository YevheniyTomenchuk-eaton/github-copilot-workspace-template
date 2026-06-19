---
applyTo: ".github/agents/**"
---

# Authoring Agent Files — AI Instructions

Rules for creating and editing custom agent definitions (`{dotted-name}.agent.md`) under `.github/agents/`.
The shared naming, encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
agent-specific delta. The VS Code `agent-customization` skill is the general authority on the file
format; read it when in doubt.

## Naming — Dot-Path Mirroring (Flat Folder)

An agent's filename **encodes the project folder it operates on** as a dot-path, exactly like
prompts, templates, and hooks — but the file sits **flat** in `.github/agents/`, never in nested
subfolders. An agent for `toolkit/dev/` is `toolkit.dev.agent.md`; a code-review variant adds one
trailing descriptor segment, `toolkit.dev.cr.agent.md`.

**Repo-wide exception:** an agent that genuinely spans the whole repository — not tied to a single
project folder — uses a simple name with no dot-path (e.g. `general.agent.md`). Reach for this only
when the agent truly has no home folder, never as an escape hatch to avoid the dot-path.

## Frontmatter

Every agent file starts with a YAML frontmatter block:

```yaml
---
name: general
description: "General-purpose assistant aware of this workspace's conventions. Use for any task: authoring, research, or running the workspace prompts."
---
```

- **`name`** (required) — the agent identifier used to invoke it. It **must exactly match the
  filename stem** (the full dotted name for a folder-scoped agent, or the simple name for a
  repo-wide one). Each dot-separated segment is lowercase kebab-case.
- **`description`** (required) — one or two sentences on the agent's purpose and scope. Surfaced in
  the agent picker and used for routing.
- **Never add a `model` key.** The model is chosen by the person running the agent; pinning models
  in the file makes them go stale and greys out the agent when those models are unavailable.

## Body

The body is the **system prompt** for that agent mode — the persona, scope, intent-detection table,
and the prompts/skills it should delegate to. Keep it declarative.

## Keep Agents Declarative — Never Inline Logic

Per the **Script it or template it** Universal Rule, an agent body must not embed multi-line
shell / PowerShell / Python snippets or full file skeletons. Delegate executable steps to prompts
that call scripts under `.github/scripts/`, and reference templates under `.github/templates/` for
file shapes. If the same logic appears across agents, extract it to one canonical script.

### CI enforcement and the example marker

The [`check-customization-inline-logic`](../../../workflows/check-customization-inline-logic.yml) workflow
fails the build when an agent file embeds a **reusable script** (a fenced executable block with
loop/function logic or many lines) or an **inline file template** (a frontmatter-plus-heading or
multi-heading skeleton). Short single-command examples and blocks that *call* a `.github/scripts/`
or `.github/templates/` artifact pass automatically. When a block is genuinely illustrative and
cannot be a call, exempt it with an example marker on the line immediately above the opening fence:

````text
<!-- example -->
```bash
git status   # illustrative only — not the prescribed call
```
````

## Encoding

UTF-8 without BOM, CRLF line endings, emojis preserved — same as all repository markdown.
