---
applyTo: ".github/instructions/**"
---

# Authoring Instruction Files — AI Instructions

Rules for creating and editing `.instructions.md` files under `.github/instructions/`. The shared
naming, encoding, and **Script it or template it** rules live in
[`.github/copilot-instructions.md`](../../../copilot-instructions.md) — this file only adds the
instruction-specific delta. The VS Code `agent-customization` skill is the general authority on the
file format; read it when in doubt.

## Frontmatter

Every instruction file starts with a YAML frontmatter block whose only key is `applyTo`:

```yaml
---
applyTo: "gaps/**"
---
```

- **`applyTo`** (required) — a glob (or comma-separated globs) matched against **workspace-relative**
  file paths. The instruction auto-loads whenever a matching file is opened or edited. Use `"**"` for
  cross-cutting standards that apply everywhere.

## Naming & Structure

- `.github/instructions/` **mirrors the project folder structure**. An instruction for
  `gaps/foundation/statuses/` lives at `.github/instructions/gaps/foundation/statuses/`. An
  instruction that governs a `.github/` subfolder mirrors that path too, with the leading `.github`
  segment encoded without its dot — e.g. one governing
  `.github/skills/**` lives at `.github/instructions/github/skills/`.
- File name is the dot-joined path plus the `.instructions.md` suffix
  (e.g. `gaps.foundation.statuses.instructions.md`). The dot-prefix must encode the full directory
  path — never skip, reorder, or abbreviate segments. A path segment whose name begins with a dot
  (such as `.github`) is encoded **without its leading dot** — the dot is the segment separator, so
  `.github/skills/` becomes `github.skills`, never `.github.skills` (see the Leading-dot rule in
  `copilot-instructions.md`).
- When one directory needs multiple instruction files, add a descriptor:
  `{path}.{descriptor}.instructions.md`.

## Keep Instructions Declarative — Reference, Don't Duplicate

- An instruction describes **when** and **how** to do something; it does not restate rules that
  already live in `copilot-instructions.md` or another instruction file. Link to the canonical home
  instead of copying.
- When an instruction tells the AI to create a file with a fixed shape, **link to a template** under
  `.github/templates/` rather than spelling out the skeleton. The instruction owns the *when/how*;
  the template owns the *shape*.
- When an instruction would otherwise embed multi-step executable logic, point at a script under
  `.github/scripts/` instead (see the **Script it or template it** Universal Rule).
- If the same guidance appears in two or more instruction files, that is a defect — consolidate it
  into one canonical file and reference it.

### CI enforcement and the example marker

The [`check-customization-inline-logic`](../../../workflows/check-customization-inline-logic.yml) workflow
fails the build when an instruction embeds a **reusable script** (a fenced executable block with
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
