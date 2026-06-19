---
applyTo: ".github/agents/**"
---

# Authoring Agent Files — AI Instructions

Rules for creating and editing custom agent definitions (`{name}.agent.md`) under `.github/agents/`.
The shared naming, encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
agent-specific delta. The VS Code `agent-customization` skill is the general authority on the file
format; read it when in doubt.

## Frontmatter

Every agent file starts with a YAML frontmatter block:

```yaml
---
name: researcher
description: "Research assistant. Gathers information from the web and the workspace, summarizes findings, and drafts documents — read-only, never edits code."
model: [claude-opus-4.6, claude-sonnet-4]
---
```

- **`name`** (required) — the agent identifier used to invoke it. Lowercase kebab-case, must match
  the file name (`{name}.agent.md`).
- **`description`** (required) — one or two sentences on the agent's purpose and scope. Surfaced in
  the agent picker and used for routing.
- **`model`** (required) — an ordered array of model ids; the first available is used, the rest are
  fallbacks.

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
