---
name: github-conventions
description: "Decide WHICH .github/ customization artifact to create (instruction, agent, skill, template, script, or hook), WHERE to put it, and HOW to name it in this repo. Covers: the artifact decision matrix, the dot-path mirroring naming rule, per-type frontmatter, the example marker, hook registration in settings, and the two CI validators (structure + inline-logic). Use when: creating or moving a file under .github/, asking 'is this an instruction or a skill?', 'what do I name this file?', 'where does this go?', or fixing a structure/inline-logic CI failure. DO NOT USE FOR: the generic VS Code file FORMAT (the built-in agent-customization skill owns that) or non-.github content authoring."
---

# .github/ Customization Conventions

Router and decision guide for authoring files under `.github/` in this repo. The authoritative rules
live in the files this skill links to — it does **not** restate them. Its job is to get you to the
right canonical file fast, then make you run the validators.

- **Shared rules** (naming, encoding, folder mirroring, "Script it or template it"):
  [`.github/copilot-instructions.md`](../../copilot-instructions.md).
- **Generic VS Code file format** (frontmatter keys, syntax): the built-in `agent-customization` skill.

## When to Use

Any time you create, move, rename, or fix a file under `.github/instructions/`,
`.github/agents/`, `.github/skills/`, `.github/templates/`, `.github/scripts/`, or `.github/hooks/` —
or when a `Check .github/ Structure` or `check-customization-inline-logic` CI job fails.

## Step 1 — Pick the artifact type

> 🚫 **Prompts are retired.** This repository has no `.github/prompts/` folder — every `/command` is
> a **skill**, invoked as `/name` exactly like a prompt *and* auto-matched by its `description`.
> The `Check .github/ Structure` workflow **fails the build** (`prompt-file-retired`) on any file
> under `.github/prompts/` or any `*.prompt.*` file, so never create one. Skills also compose:
> several can be used in a single chat window, and the agent loads them dynamically as the work
> requires.

| You want to… | Use a… | Lives under | Authoring guide |
|---|---|---|---|
| Auto-apply rules whenever certain files are edited | **instruction** | `.github/instructions/` | [github.instructions.instructions.md](../../instructions/github/instructions/github.instructions.instructions.md) |
| Give the user a `/command`, or package reusable domain knowledge auto-invoked by task match | **skill** | `.github/skills/<name>/SKILL.md` | [github.skills.instructions.md](../../instructions/github/skills/github.skills.instructions.md) |
| Define a selectable agent persona/mode | **agent** | `.github/agents/` | [github.agents.instructions.md](../../instructions/github/agents/github.agents.instructions.md) |
| Provide a fixed file skeleton the AI fills in | **template** | `.github/templates/` | shared rules in [copilot-instructions.md](../../copilot-instructions.md) |
| Provide reusable executable logic that skills call | **script** | `.github/scripts/<domain>/` | [scripts/github/README.md](../../scripts/github/README.md) |
| Run an automation when a lifecycle event fires | **hook** | `.github/hooks/` (flat) | [github.hooks.instructions.md](../../instructions/github/hooks/github.hooks.instructions.md) |

Quick disambiguation:

- **instruction vs skill** — an instruction fires automatically by `applyTo` glob; a skill is either
  invoked explicitly as `/name` or auto-matched by its `description`. Rules that must always hold →
  instruction; something you *do* or *look up* → skill.
- **the two shapes of a skill** — a *recipe* (a runnable `/command`, the role prompts used to fill)
  and *know-how* (reference knowledge pulled in on task match). One skill may be both.
- **template vs script** — a template owns a file's *shape*; a script owns *executable logic*.
  Never inline either into a skill/instruction/agent body (see Step 4).
- **script vs hook** — a script *is* the logic; a hook is the JSON binding that runs a script when a
  lifecycle event fires. A hook never embeds logic — its `command` points at a script.

## Step 2 — Place and name it (mirroring + dot-path)

`.github/instructions/`, `prompts/`, and `templates/` **mirror the project folder structure**. A file
governing `organization/foundation/roles/` lives at the mirrored path under its type folder; a file
governing a `.github/` subfolder mirrors that too, with the leading `.github` segment encoded
without its dot (e.g. `.github/instructions/github/prompts/`).

The file name is the **dot-joined directory path** plus the type suffix — never skip, reorder, or
abbreviate path segments:

- instruction → `{dir.path.as.dots}.instructions.md` (multiple in one dir → add `.{descriptor}`)
- prompt → `{dir.path.as.dots}.{action}.prompt.md` (root-level commands use a bare name)
- template → `{dir.path.as.dots}.template.{ext}` (or `.{descriptor}.template.{ext}`)
- hook → `{dir.path.as.dots}.{descriptor}.json`, but placed **flat** in `.github/hooks/` (the
  dot-name encodes the mirrored path; the file does not sit in a mirrored subfolder)
- agent → `{name}.agent.md` · skill → `<folder>/SKILL.md`

Two rules that trip people up — both are in
[copilot-instructions.md](../../copilot-instructions.md): a path segment beginning with a dot
(such as `.github`) is encoded **without its leading dot** (`github.prompts.instructions.md`, never
`.github.prompts...`), because the dot is the segment separator; and the suffix keyword (`template`,
`prompt`, `instructions`) must appear **exactly once** — omit a path segment that would duplicate it.

## Step 3 — Frontmatter

Each type's required frontmatter keys are documented in its authoring guide linked in Step 1. Open
that guide and copy its frontmatter block. The whole file must begin **directly** with the `---`
frontmatter — never wrap it in a ` ``` ` code fence (that hides the frontmatter and the CI structure
check flags it as `leading-fence-wrapper`).

## Step 4 — Keep it declarative (the inline-logic rule)

Prompts, instructions, and agents must **not** embed reusable multi-line shell/PowerShell/Python or
full file skeletons. Extract logic to `.github/scripts/` and **call** it; extract skeletons to
`.github/templates/` and **link** to them. Skills (this file's type) are exempt from CI enforcement
but follow the same spirit. When a fenced block is genuinely illustrative, exempt it with an example
marker on the line directly above the opening fence:

````text
<!-- example -->
```bash
git status   # illustrative only — not the prescribed call
```
````

## Step 5 — Validate before shipping

Run these validators from the repo root and fix everything they report:

```pwsh
python .github/scripts/check-github-structure.py .
python .github/scripts/check-customization-inline-logic.py .
python .github/scripts/check-powershell-conventions.py .
```

What they enforce:

- **[check-github-structure](../../workflows/check-github-structure.yml)** — naming/placement/mirroring,
  frontmatter presence, kebab-case, duplicate/duplicate-keyword suffixes, misplaced files, the
  `leading-fence-wrapper` check, the `prompt-file-retired` ban on any reintroduced prompt artifact,
  and hook JSON validity (valid JSON, a top-level `hooks` object, recognised event names).
- **[check-customization-inline-logic](../../workflows/check-customization-inline-logic.yml)** — fails
  on inlined reusable scripts or file skeletons in instructions/agents (skills excluded).
- **[check-powershell-conventions](../../workflows/check-powershell-conventions.yml)** — the four
  `.ps1` helper rules from [copilot-instructions.md](../../copilot-instructions.md): `-NoProfile
  -NonInteractive` at every launch site, `$(throw)` defaults instead of `Mandatory` parameters,
  pure-ASCII script bodies, and Git capture only through `invoke-git-command.ps1`. Run it whenever
  you add or call a `.ps1` helper.

`check-github-structure` runs on PRs (delta) and on push-to-main / manual dispatch (full scan).
`check-customization-inline-logic` and `check-powershell-conventions` run **delta-only** on PRs
*and* push-to-main (only the changed files are audited), so pre-existing debt is grandfathered; a
full-tree audit happens via manual `workflow_dispatch`. `check-powershell-conventions` escalates to
a full scan by itself whenever its own checker or workflow changes, since that alters how every
file is judged.

## Step 6 — Register and encode

- New `/command` skill → add it to the **Workspace Skills** table in
  [workspace/README.md](../../../workspace/README.md).
- New hook in a deliberately nested subfolder → add its folder to `chat.hookFilesLocations` in
  [.vscode/settings.json](../../../.vscode/settings.json). Flat `.github/hooks/*.json` files need no
  registration — that folder is registered by default.
- All files: UTF-8 without BOM, CRLF line endings, emojis preserved.
