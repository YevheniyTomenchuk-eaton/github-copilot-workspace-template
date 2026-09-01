---
name: create-customization
description: "Create or update any .github/ customization (instruction, agent, skill, template, script, or hook) the right way for this repo. Figures out which artifact(s) the request actually needs — often more than one — then places, names, registers, and validates them per our conventions. Use when: the user says 'create an instruction/agent/skill/template/script/hook', 'add a /command', 'capture this workflow', 'make a rule for X', 'automate this', or runs any /create-* idea. Also handles requests phrased as 'create a prompt' — prompts are retired, so those become skills."
---

# Create Customization

Turn a request like *"capture this workflow"*, *"make a rule for the toolkit folder"*, or
*"automate this check"* into the **correct set** of `.github/` customization files for this
repository — created in the right folders, with the right names, registered, and validated.

This is the repo-aware replacement for VS Code's built-in `/create-instruction`,
`/create-skill`, `/create-agent`, and `/create-hook` commands. Those built-ins
produce format-valid files but ignore this repo's mirrored folders, dot-path names, registration,
and CI validators. This command does not — it routes every decision through the
[`github-conventions`](../github-conventions/SKILL.md) skill, which is the single source of
truth for **which** artifact, **where** it lives, **how** it is named, and **how** it is validated.

> 🚫 **Never create a prompt file.** Prompts are retired: `.github/prompts/` does not exist, and the
> structure validator fails the build (`prompt-file-retired`) on any `*.prompt.*` file. When a user
> asks for "a prompt", they mean a `/command` — **create a skill**, which is invoked the same way
> (`/<name>`), is additionally auto-matched by its `description`, and can be combined with other
> skills in one chat window. Say so plainly when you make that substitution.

> 🧠 **Be smart about scope.** One request often needs **more than one** artifact. A "new
> `/command`" that does real work is usually a **skill** *plus* a **script** it calls (logic is
> never inlined) — and possibly a **template** for the files it generates and an **instruction**
> that auto-applies rules when those files are edited. Evaluate the whole need, not just the word
> the user used.

## What to do

1. **Load the conventions skill.** Read [`github-conventions`](../github-conventions/SKILL.md)
   first and follow it for every decision below. Do not restate its rules — apply them.

2. **Understand the real intent.** If the request is vague, ask the user a few selectable
   clarifying questions before creating anything: what should happen, when it should apply
   (a `/command`? an automatic rule? an event?), and what folder/domain it concerns.

3. **Decide the artifact set (Step 1 of the skill).** Using the skill's decision matrix, choose
   **all** the artifact types this need requires — not just one:

   | Need | Artifact |
   |------|----------|
   | Auto-apply rules when certain files are edited | **instruction** (`applyTo` glob) |
   | A `/command` the user runs on demand | **skill** (the recipe shape) |
   | Reusable domain know-how auto-matched by task | **skill** (the know-how shape) |
   | A selectable expert persona/mode | **agent** |
   | A fixed file skeleton the AI fills in | **template** |
   | Reusable executable logic a skill calls | **script** |
   | An automation that fires on a lifecycle event | **hook** (`.github/hooks/*.json`) |

   Note that a skill covers both the *runnable command* and the *reference knowledge* case, and one
   skill can be both. State the chosen set back to the user before writing files, so they can
   confirm the scope.

4. **Optionally draft content with the built-ins.** You may use VS Code's `/create-instruction`,
   `/create-skill`, `/create-agent`, or `/create-hook` purely to *draft* body content — but you own
   placement, naming, frontmatter, registration, and validation per the skill. Never accept the
   built-in's default location or filename, and never use `/create-prompt`.

5. **Place and name each file (Step 2).** Mirror the project folder structure and use the dot-path
   filename convention, including the leading-dot rule and suffix-deduplication. Skills are the
   exception: they live flat at `.github/skills/<name>/SKILL.md` with a kebab-case name that encodes
   the mirrored path (e.g. `toolkit-email-create`). Apply the correct frontmatter for each type
   (Step 3).

6. **Keep it declarative (Step 4 — the golden rule).** Never inline a reusable script or a file
   skeleton into an instruction or agent. Extract executable logic to a **script** under
   `.github/scripts/<domain>/` and **call** it; extract repeated file shapes to a **template** and
   **link** to it. A hook's `command` must point at a script, never embed logic. When a fenced
   block is genuinely illustrative, add the `<!-- example -->` marker above it.

7. **Register and catalog.**
   - A new `/command` skill → add a row to the **Workspace Skills** table in
     [`workspace/README.md`](../../../workspace/README.md).
   - A new script → add a row to its domain `README.md` catalog under `.github/scripts/<domain>/`.
   - A new demo skill → add it to [`workspace/demo/README.md`](../../../workspace/demo/README.md).

8. **Validate before finishing (Step 5).** Run the validators from the repo root and fix
   everything they report. The third one matters whenever you added or called a `.ps1` helper —
   it catches launch flags, parameter guards, non-ASCII characters, and raw Git capture:

   ```pwsh
   python .github/scripts/check-github-structure.py .
   python .github/scripts/check-customization-inline-logic.py .
   python .github/scripts/check-powershell-conventions.py .
   ```

9. **Confirm encoding (Step 6).** UTF-8 without BOM, CRLF line endings, emojis preserved.

10. **Summarise.** List every file created or changed, which artifact type each is, why it was
    chosen, and confirm the validators passed.

## Presenter / usage notes

- Prefer **one** artifact when one is enough; reach for a multi-file set only when the need genuinely
  spans concerns (e.g. a command + its script + an auto-applied rule).
- If the request is really *"draft a hook live"* for a demo, point the user at
  `/workspace-demo-hooks-tour` instead — that skill is purpose-built for presentations.
- This command changes only `.github/` (and the README tables it must update). It never commits or
  pushes — run `/ship` when ready.
