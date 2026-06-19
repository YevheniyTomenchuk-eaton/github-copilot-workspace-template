---
applyTo: ".github/prompts/**"
---

# Authoring Prompt Files — AI Instructions

Rules for creating and editing `/command` prompt files under `.github/prompts/`. The shared
naming, encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
prompt-specific delta. The VS Code `agent-customization` skill is the general authority on the
file format; read it when in doubt.

## Frontmatter

Every prompt file starts with a YAML frontmatter block:

```yaml
---
description: "One sentence on what it does. Use when: <trigger phrases the user might say>."
agent: agent
---
```

- **`description`** (required) — drives discovery. Always include a `Use when:` clause listing the
  phrases or intents that should invoke the command.
- **`agent`** (required) — the agent the command runs under. Use `agent` for the default agent, or
  a named agent (e.g. `dev`, `qa`) when the command must run in a specific mode. (`mode: 'agent'`
  is the legacy spelling — prefer `agent:`.)

## Naming & Invocation

- File name follows the dot-path convention in `copilot-instructions.md`:
  `{path-components-joined-by-dots}.{action}.prompt.md`. Root-level cross-cutting commands use a
  bare name (e.g. `latest.prompt.md`, `ship.prompt.md`).
- The command is invoked as `/{filename-without-.prompt.md}`.
- After adding a new command, register it in the **Authoring & shipping** table in
  [`workspace/README.md`](../../../../workspace/README.md).

## Keep Prompts Declarative — Never Inline Logic

A prompt body describes **when** and **what**, never **how-as-code**. Per the **Script it or
template it** Universal Rule:

- Do **not** paste multi-line shell / PowerShell / Python snippets (API call sequences, poll loops,
  parse-and-emit steps) into the prompt body. Extract them to
  `.github/scripts/<domain>/<name>.{ps1,py}` and have the prompt **call** the script, parsing its
  `KEY=value` output. See [`.github/scripts/github/README.md`](../../../scripts/github/README.md) for the
  established pattern.
- Do **not** spell out the full skeleton of a file the prompt tells the AI to create. Extract the
  skeleton to a template under `.github/templates/` and **link** to it.
- Before inlining anything, check whether a script or template already exists. If the same snippet
  appears in two or more prompts, that is a defect — extract it to a single canonical home.

### CI enforcement and the example marker

The [`check-customization-inline-logic`](../../../workflows/check-customization-inline-logic.yml) workflow
fails the build when a prompt embeds a **reusable script** (a fenced executable block with
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
