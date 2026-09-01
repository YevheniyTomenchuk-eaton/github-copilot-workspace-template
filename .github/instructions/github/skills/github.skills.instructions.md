---
applyTo: ".github/skills/**"
---

# Authoring Skill Files — AI Instructions

Rules for creating and editing reusable skill packages under `.github/skills/`. The shared naming,
encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
skill-specific delta. The VS Code `agent-customization` skill is the general authority on the file
format; read it when in doubt.

## Skills Are the Only Command Artifact

**Prompts are retired.** `.github/prompts/` does not exist and must never be recreated — the
`Check .github/ Structure` workflow fails the build (`prompt-file-retired`) on any `*.prompt.*` file.
Everything a prompt file used to do is now a skill, because a skill does strictly more:

- It is invoked **exactly like a prompt** — type `/<skill-name>` in chat.
- It is **also auto-invoked** when the agent matches a task against its `description`, so it fires
  without anyone remembering the command name.
- **Several skills can be combined in a single chat window**, and the agent loads them dynamically as
  the work requires — a prompt file could not be chained that way.
- Copilot indexes skills far better than prompt files, and the latest Visual Studio applications no
  longer support prompt files at all.

A skill therefore covers two shapes, and one skill may be either or both:

| Shape | What it is | Example |
|---|---|---|
| **Recipe** | A runnable procedure the user starts with `/<name>` — the old prompt role | `/ship`, `/validate` |
| **Know-how** | Reference knowledge the agent pulls in when the task matches, with no command typed | `github-conventions`, `office-documents` |

Instructions remain distinct: an **instruction** is a standing rule that applies automatically to
whatever files its `applyTo` glob matches. A skill is knowledge or a procedure that is *invoked* —
by name or by task match. When in doubt: rules that must always hold → instruction; something you
*do* or *look up* → skill.

## Structure

- Each skill lives in its **own subfolder** under `.github/skills/` and contains a `SKILL.md` file
  (e.g. `.github/skills/github/SKILL.md`).
- Supporting assets (scripts, templates, reference data) the skill needs may live alongside `SKILL.md`
  in the skill folder, **or** be referenced from the shared `.github/scripts/` and
  `.github/templates/` trees when they are useful beyond this one skill.

## Frontmatter

```yaml
---
name: github
description: "What the skill covers and WHEN to use it. Covers: <topics>. Use when: <triggers>. DO NOT USE FOR: <exclusions>."
---
```

- **`name`** (required) — lowercase kebab-case, matches the folder name.
- **`description`** (required) — this is the **invocation trigger**. The agent auto-invokes the skill
  by matching the task against this text, so it must enumerate the topics covered, the concrete
  situations that should invoke it, and (when helpful) what it is **not** for. A vague description
  means the skill never fires.

## Keep Skills Declarative — Never Inline Logic

Per the **Script it or template it** Universal Rule:

- A `SKILL.md` body must **not** embed *reusable, multi-step* shell / PowerShell / Python logic.
  Extract such logic to scripts (in the skill folder or `.github/scripts/<domain>/`) and have the
  skill **call** them, parsing their `KEY=value` output. See
  [`.github/scripts/github/README.md`](../../../scripts/github/README.md). Short, illustrative
  single-purpose command examples are fine and encouraged.
- A `SKILL.md` must **not** spell out full file skeletons it tells the AI to create — link to a
  template under `.github/templates/` instead.
- If the same snippet or skeleton appears in this skill and elsewhere, that is a defect — extract it
  to one canonical home and reference it.

### CI enforcement

Skills are **exempt** from the [`check-customization-inline-logic`](../../../workflows/check-customization-inline-logic.yml)
workflow that gates instructions and agents — a skill is a reference document and may contain as
many short command examples as it needs. The extraction/deduplication guidance above (which targets
*reusable multi-step logic*, not illustrative one-liners) is still the expectation for skills, just
not CI-enforced.

## Registration

After adding a skill that exposes a `/command`, register it in the workspace tables in
[`workspace/README.md`](../../../../workspace/README.md) so people can discover it. Demo skills go in
[`workspace/demo/README.md`](../../../../workspace/demo/README.md) instead.

## Encoding

UTF-8 without BOM, CRLF line endings, emojis preserved — same as all repository markdown.
