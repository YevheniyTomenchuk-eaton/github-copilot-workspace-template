# GitHub Copilot Workspace Template — Copilot Instructions

## AI Memory Policy

**Never create or update user memory (`/memories/`) or repo memory (`/memories/repo/`).** All persistent knowledge belongs in `.github/instructions/` files — not in hidden memory. Session memory (`/memories/session/`) is acceptable for in-conversation scratch notes only.

## What Is This Repository?

This is a **template** for building your own GitHub Copilot-powered workspace — a place where you teach Copilot your conventions once (through instructions, skills, agents, templates, and scripts) and then let it do repeatable work for you. Clone it, open it in VS Code, and start adding your own content and customizations.

It is also a **GitHub Pages** site (Jekyll + [just-the-docs](https://just-the-docs.com/README.md)), so any Markdown you add is automatically published as a searchable documentation site with a sidebar, navigation, diagrams, and math support.

You do not have to use every part. Keep what helps, delete what you don't need. The two things worth keeping in any case are the **`.github/` conventions** (how customization files are named and organized) and the **CI checks** that keep your content consistent.

## The Foundation Pattern (optional convention)

A pattern this template demonstrates — adopt it if it fits, ignore it if not.

The idea: anything that has a **canonical definition** gets its own definition file, and everywhere else you **link to that file** instead of repeating its value as plain text. This keeps a single source of truth and lets the published site cross-link automatically.

**Plain text (no single source of truth):** `Status: in-progress`
**Linked to a definition file:** `**Status:** [in-progress](../foundation/statuses/in-progress.md)`

If you organize content into domains (e.g. `notes/`, `decisions/`, `guides/`), each domain can carry its own conventions in a matching `.github/instructions/` file. This is a convention, not a requirement — the CI checks do not force you to create any particular folder.

## Universal Rules

These apply to all content you add. They are what the CI checks enforce.

**Linking:** When you do link to another file, use relative paths. Prefer linking over duplicating a value that lives in a definition file.

**Naming:** Lowercase kebab-case for all files and folders.

**Markdown tables:** Always leave a blank line before and after every table. Never place a heading directly above or below a table row — the blank line is required for proper rendering. Never create empty tables (header + separator with no data rows) — a table must always have at least one data row. If there is no data yet, use an italic placeholder (e.g., `*No items yet.*`) instead of an empty table. Every data row must have the same number of columns as the header row — column count mismatches corrupt the table. If cell content contains a literal pipe character (`|`), escape it as `&#124;`.

**Math formulas:** Use MathJax syntax — `$...$` for inline math, `$$...$$` for display math. The site loads MathJax v3 via `_includes/head_custom.html`. Display math (`$$...$$`) **must** have a blank line before and after — kramdown only recognizes block-level math when isolated as its own paragraph.

**How kramdown + MathJax v3 interact:** `_config.yml` sets `kramdown: math_engine: null` — this makes kramdown emit math using standard LaTeX delimiters (`\[...\]`, `\(...\)`) instead of `<script type="math/tex">` tags (which MathJax v3 cannot read). The MathJax config in `_includes/head_custom.html` recognizes **both** raw delimiters (`$...$`, `$$...$$`) and kramdown-converted delimiters (`\(...\)`, `\[...\]`). **Never remove either setting** — removing `math_engine: null` breaks display math, and removing the `\[...\]` / `\(...\)` entries breaks kramdown-converted formulas.

**Diagrams:** Mermaid only (no image files). Follow [diagram-standards.instructions.md](instructions/diagram-standards.instructions.md).

**Mermaid line breaks:** In Mermaid node and edge labels, `\n` is **not** a line break — it renders as the literal text `\n`. Always use `<br/>` for line breaks. **When using `<br/>` in a node label, always wrap the label in double quotes:** `NODEID["Line 1<br/>Line 2"]`.

**Mermaid no double curly braces:** Never use Mermaid's hexagon shape {% raw %}`{{ }}`{% endraw %} on Jekyll sites. Jekyll's Liquid template engine processes {% raw %}`{{ }}`{% endraw %} as variable output before Mermaid sees the diagram, causing "Syntax error in text". Use a diamond `{ }` or stadium `([ ])` instead. This does **not** show up in VS Code's local Mermaid preview because VS Code does not run Liquid.

**Documentation states facts only — never reference edit history.** When correcting an error in a file, simply write the correct information. Never include phrases like "previously this was incorrect", "corrected from…", or any self-referential commentary about past mistakes. This is published documentation, not a changelog.

**Don't invent things.** If you're not sure a value, link target, or operational detail exists — check first or ask the user. Never fabricate metadata, URLs, or process details that haven't been verified.

**Update parent README.** After creating a new entry in a domain, add it to that domain's `README.md` table if it maintains one.

**Script it or template it — never inline it.** Instructions, agents, and skills must stay declarative. Any reusable, multi-step, or error-prone logic belongs in an extracted artifact referenced everywhere — not pasted as plain text:

- **Executable logic → a script.** If a skill or instruction would otherwise embed a shell/PowerShell/Python snippet (an API call sequence, a poll loop, a parse-and-emit step, a validation pass), extract it to `.github/scripts/<domain>/<name>.{ps1,py}` and have the skill **call** it. Scripts emit machine-readable `KEY=value` lines so callers parse output deterministically. See [`.github/scripts/github/README.md`](scripts/github/README.md) for the established pattern.
- **Repeated file shapes → a template.** If a skill or instruction would otherwise spell out the full skeleton of a file it tells the AI to create, extract that skeleton to `.github/templates/<path>.template.{md,ext}` and have the instruction **link** to it.
- **Deduplicate aggressively.** Before inlining anything, check whether a script or template already exists. If the same snippet or skeleton appears in two or more places, extract it. Each piece of logic and each file shape has exactly one canonical home.
- **Reference, don't duplicate.** When the logic changes, only the canonical artifact changes — every consumer stays correct automatically.

**No scratch files at the repo root.** Never create temporary logs, helper scripts, dumps, or ad-hoc files at the repository root (e.g. `clone.log`, scratch `.json` / `.gql` / `.ps1` files). The repo root is reserved for tracked project files only. When a tool needs a temporary file, write it under the system temp directory (`$env:TEMP`) or a gitignored subfolder.

**PowerShell helper rules.** Agent-run `.ps1` helpers under `.github/scripts/` have four hard rules. Each exists because breaking it produces a failure that is silent, machine-dependent, or hangs the agent outright. All four are enforced in CI by [`check-powershell-conventions.py`](scripts/check-powershell-conventions.py) (workflow [`check-powershell-conventions.yml`](workflows/check-powershell-conventions.yml)), which runs delta-only on pull requests and in full on demand.

- **Always launch `.ps1` helpers with `-NoProfile -NonInteractive`** *(Rule B, call site)*. When a skill starts a helper in a **new** PowerShell process, it must use the full form: `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "<script>" ...`. Launched with `-File` but **without** `-NonInteractive`, a missing or misspelled required parameter makes PowerShell silently drop into an interactive `Supply values for the following parameters:` prompt and **hang forever** in an agent session; `-NonInteractive` turns that same mistake into an immediate, loud error. The **only** exception is a script *designed* to prompt at the console (`Read-Host`, `Get-Credential`, an interactive web login) — those must **omit `-NonInteractive`** so their prompts can appear, while still carrying `-NoProfile`. Adding the flag to an interactive script makes its prompt **throw** instead of appearing.
- **Guard required parameters with a `$(throw)` default** *(Rule A, script side)*. `-NonInteractive` only protects callers who remember the flag; the caller-independent complement is a throwing default: `[string]$Owner = $(throw 'Required parameter -Owner was not provided.')`. The default expression runs **only** when the argument is omitted, so it fails fast and self-describes in any host — never a hang. A parameter cannot be both `[Parameter(Mandatory = $true)]` and carry a throwing default, so **replace** the Mandatory attribute; keep any `[ValidateSet]` / `[ValidatePattern]` validators, which run on supplied values. This applies to interactive scripts too — the throw fires only on omission, leaving the body's own prompts untouched. Exempt: parameters using `ParameterSetName` (conditional mandatoriness), and nested helper functions in dot-sourced libraries (never invoked via `-File`, so they cannot hang). For a rare legitimate exception, carry the `# ps-conventions:allow-mandatory` marker; prefer the throwing default.
- **Keep agent-run `.ps1` helpers pure ASCII** *(Rule C)*. These scripts are launched through `powershell.exe` (Windows PowerShell 5.1), which reads a BOM-less source file with the **machine's ANSI code page**, not UTF-8. A literal non-ASCII character (em-dash, ellipsis, arrow, accented letter, emoji) is decoded from its raw UTF-8 bytes into the wrong glyphs; when those bytes land on a structural character (quote, brace, paren) the file fails to tokenize and the helper dies with a syntax error that **never reproduces** on a UTF-8 host. Write these scripts in plain ASCII and emit any runtime non-ASCII with an escape — `[char]0x2014` for an em-dash, `[char]::ConvertFromUtf32(0x1F512)` for an emoji. This is the one place the "preserve emojis" rule below does **not** apply.
- **Capture Git output through the shared helper** *(Rule D)*. Under Windows PowerShell 5.1, a direct `$output = & git ... 2>&1` in a script with `$ErrorActionPreference = 'Stop'` can throw `NativeCommandError` when Git writes ordinary progress to stderr — even when Git exits successfully. Dot-source [`.github/scripts/github/invoke-git-command.ps1`](scripts/github/invoke-git-command.ps1), call `Invoke-GitCommand`, and decide success from its `ExitCode`; use its normalized `Output` only for diagnostics or parsing. Ordinary uncaptured Git calls may still check `$LASTEXITCODE` directly. That helper is the only script allowed to capture Git with `2>&1`.

**Never push to `main` directly.** All changes go through a pull request. Never run `git commit` or `git push` on your own — wait for the user to invoke **`/ship`**, which handles branching, committing, pushing, and PR creation. The `/ship` workflow uses **terminal commands only** (`git` and `gh` CLI).

**Never discard uncommitted work.** These commands destroy work and must NEVER be run without explicit user permission: `git stash`, `git stash drop`, `git clean`, `git checkout -- .`, `git restore .`, `git reset --hard`. If you need to switch branches, commit and push first.

## `sources/` — Local Reference Material

The optional `sources/` folder is a local, gitignored place to drop **reference material you want the AI to read and analyze** — source code, data exports, specs, large documents, anything too big or too private to publish. It is **gitignored** and **excluded from Jekyll**, so nothing in it is committed or appears on the published site.

**Purpose:** Give the AI real context for source-level analysis — verifying facts, tracing how something works, comparing versions, or pulling details out of a large file — without polluting the knowledge base.

**When to search `sources/`:** Only when the task needs that reference material. Use `grep_search` with `includeIgnoredFiles: true` and `includePattern: "sources/**"` to search within it.

**When NOT to search `sources/`:** During normal content editing. Default searches should NOT include `sources/` to avoid noise.

## YAML Front Matter (GitHub Pages Navigation)

This site uses the **just-the-docs** Jekyll theme. Every published markdown file **must** start with YAML front matter (`---` block) so the theme can build sidebar navigation, search index, and breadcrumbs.

### Required Keys

| Key | Required | Description |
|---|---|---|
| `title` | **Always** | Human-readable page title. Appears in sidebar, browser tab, and search results. Always double-quoted. |
| `parent` | On child pages | Must **exactly match** the `title` of the parent page. This creates the sidebar hierarchy. |
| `grand_parent` | When parent title is non-unique | Must **exactly match** the `title` of the grandparent page. Required when multiple pages share the same `parent` title. |
| `nav_order` | On section pages | Integer controlling sidebar sort order. Lower numbers appear first. |
| `has_toc` | Optional | Set to `false` on section pages to hide the in-page table of contents. |
| `permalink` | Only on root | Set to `/` on `README.md` at the repository root. |

### Title Rules

- **Clean title** — strip emoji prefixes from H1 headings (e.g., H1 `📊 Notes` → title `"Notes"`).
- **Title must match H1** — the `title` in front matter and the `# H1` heading must use the same text (after emoji stripping).
- **Always double-quote** — protects against YAML-special characters (`#`, `:`, digits).
- **Unique within siblings** — no two pages under the same parent should share a title.
- **Preserve special characters in titles** — arrows (`→`), em-dashes, etc. must appear in the title.

### `grand_parent` — Disambiguating Non-Unique Parent Titles

just-the-docs supports **3 levels** of hierarchy: `title` → `parent` → `grand_parent`. When a page's `parent` title exists on more than one page, `grand_parent` resolves the ambiguity by specifying the parent's parent. To determine the value, look at the parent page's front matter and use its `parent` value as your `grand_parent`.

### Suffix Pattern — When `grand_parent` Cannot Disambiguate

When two pages share the same `title`, `parent`, AND `grand_parent`, add a disambiguating suffix to the title — e.g., `Name (Context)`. Always use **suffix** (not prefix).

### Page Patterns

**Section page** (top-level `README.md`):
```yaml
---
title: "Notes"
nav_order: 1
has_toc: false
---
```

**Sub-section page** (folder `README.md` under a section):
```yaml
---
title: "Meeting Notes"
parent: "Notes"
---
```

**Leaf content page**:
```yaml
---
title: "2026-06-18 standup"
parent: "Meeting Notes"
---
```

**Root homepage** (`README.md` at repo root):
```yaml
---
title: "Home"
permalink: /
---
```

### When Creating a New File

1. Add YAML front matter with `title` and `parent` (matching the parent page's exact `title`).
2. If the page's `title` or `parent` title is non-unique across the site, add `grand_parent`.
3. The file automatically appears in the sidebar under its parent — no other configuration needed.

### No Hardcoded Child Lists

The sidebar **automatically** shows all child pages under their parent. Never duplicate this with hardcoded bullet lists or tables of child links in a README. Use README space for descriptive content the sidebar cannot provide (overview tables with extra columns, diagrams, rules). Dashboard-style tables in top-level READMEs that add curated context (status, description columns) are acceptable.

### No Manual Navigation

Navigation is handled entirely by YAML front matter (`title` + `parent`). The theme generates sidebar, breadcrumbs, and hierarchy automatically. **Never** add manual navigation sections, back-links, or breadcrumbs inside page content (including `---` horizontal-rule separators used to set off a navigation footer).

**Exception — sequential reading-order tables in linear guides.** A small set of pages form a deliberately ordered, start-to-finish reading sequence (e.g., the `workspace/using-copilot/` guide). On those pages only, a **Previous / Next table** is allowed, because the sidebar conveys hierarchy but not reading order. The table must contain only the adjacent Previous and Next pages. The series entry page may additionally carry **one** curated index table listing the pages in reading order.

### Sidebar Sort Order (`nav_order`)

By default, just-the-docs sorts sidebar items **alphabetically by title**. Use `nav_order` when items have a **logical non-alphabetical order** (lifecycle stages, severities, priorities, versions). Pages without `nav_order` sort alphabetically.

## `.github/` Folder Convention

Everything inside `.github/` **mirrors the project folder structure**. This applies to all `.github/` subfolders:

- **`.github/instructions/`** — AI instruction files. Each subfolder matches a project domain. Instruction files use `applyTo:` frontmatter to activate automatically when working in the matching folder. File naming: `{path-components-joined-by-dots}.instructions.md`. When a directory contains multiple instruction files, add a descriptor: `{path}.{descriptor}.instructions.md`.
- **`.github/prompts/`** — **Does not exist, and must never be recreated.** Prompts are retired: every `/command` is a **skill** under `.github/skills/`. A skill is invoked as `/name` exactly like a prompt was, is **also** auto-matched by its `description` so it fires without the command being typed, and **several skills can be combined in one chat window** with the agent loading them dynamically. Copilot indexes skills far better than prompt files, and the latest Visual Studio applications no longer support prompt files at all. The `Check .github/ Structure` workflow fails the build (`prompt-file-retired`) on any `*.prompt.*` file or anything under `.github/prompts/`.
- **`.github/templates/`** — Template files (skeletons for new content). File naming follows the same dot-notation with `.template.md` (or `.template.{ext}`):
  - Simple template → `{path}.template.md`
  - Named template → `{path}.{descriptor}.template.md`
  - Non-markdown → `{path}.template.{ext}`
  - **Deduplication rule:** The word `template` must appear **exactly once** in the filename — only as the suffix. If a path component is literally `template/`, omit it from the dot-prefix.
- **`.github/agents/`** — Custom agent definition files (`{dotted-name}.agent.md`). Like templates and hooks, an agent's filename **encodes the project folder it operates on** as a dot-path, but the file sits **flat** in `.github/agents/` (e.g. `toolkit.dev.agent.md` would drive `toolkit/dev/`). An agent that is **repo-wide** — genuinely not tied to a single project folder — uses a simple name with no dot-path (e.g. `general.agent.md`); reach for this only when the agent truly spans the whole repo. YAML frontmatter has `name` and `description`. The `name` **must exactly match the filename stem**, and that same value is how the agent is invoked. **Never add a `model` key** — the model is chosen by the person running the agent.
- **`.github/skills/`** — Reusable skill packages, and the **only** command artifact in this repository. Each skill lives in its own subfolder with a `SKILL.md` file. Skills sit **flat** in `.github/skills/` — they do **not** mirror the project folder tree; the lowercase kebab-case folder name encodes the mirrored path instead (e.g. `toolkit/email/` plus the action `create` → `toolkit-email-create`). A skill is invoked as `/<name>` **and** auto-invoked when the agent matches a task against its `description`. It has two shapes, and one skill may be both: a **recipe** (a runnable `/command` — the role prompt files used to fill) and **know-how** (reference knowledge pulled in on task match). This is what separates a skill from an instruction, which is a standing rule auto-applied by its `applyTo` glob.
- **`.github/scripts/`** — Extracted executable logic referenced by skills, instructions, and hooks. Each subfolder matches a domain. Scripts emit machine-readable `KEY=value` lines so callers parse output deterministically, and each domain folder carries a `README.md` cataloguing its scripts.
- **`.github/hooks/`** — Agent hook definition files (`*.json`) that bind a VS Code lifecycle event (`PreToolUse`, `PostToolUse`, …) to a command. Like templates, each hook uses the dot-path filename, but the file sits **flat** in `.github/hooks/` (e.g. `.github/hooks/workspace.demo.hooks-tour.json` encodes `workspace/demo/`). The command a hook runs is a **script** under `.github/scripts/`, never inlined logic. VS Code's hook loader is **single-level per folder** (no `**` recursion), so flat placement keeps every hook in the default-registered `.github/hooks` folder; only a deliberately nested subfolder needs its own `chat.hookFilesLocations` entry in `.vscode/settings.json`.

**Naming rule:** The dot-prefix in the filename **must encode the directory path** from the subfolder root to the file's parent directory, with `/` replaced by `.`. The filename must never skip, reorder, or abbreviate path segments. If a path component would cause a keyword to repeat (e.g., `template` in the path and as the suffix), omit the path component. For agents, the encoded path is the **project folder the agent operates on** (the only exception is a genuinely repo-wide agent, which uses a simple name); for everything else it is the file's own mirrored location.

**Leading-dot rule:** A `.` is the dot-prefix **segment separator**, so a path segment whose name begins with a dot (e.g. the `.github` folder itself) is encoded **without its leading dot** — in **both** the dot-prefix filename **and** the mirrored directory path: `.github/skills/` → `github.skills` (filename) and `.github/instructions/github/skills/` (directory), never `.github.skills` or a nested literal `.github` folder. Example: a file governing `.github/skills/**` lives at `.github/instructions/github/skills/github.skills.instructions.md`.

Instruction files link to their corresponding template files using relative paths. When creating a new item:
1. The matching `.instructions.md` file is automatically loaded (via `applyTo:` frontmatter).
2. Follow the instruction file's guidance — it links to the relevant template(s).
3. Copy the linked template as the starting point.

**Never** create `.template.md` files in project folders. Templates and instructions live exclusively in `.github/`.

**Authoring these customization files is itself governed by instruction files** under `.github/instructions/github/`, each auto-loading via its `applyTo` glob: [`github.instructions.instructions.md`](instructions/github/instructions/github.instructions.instructions.md) (`.github/instructions/**`), [`github.agents.instructions.md`](instructions/github/agents/github.agents.instructions.md) (`.github/agents/**`), [`github.skills.instructions.md`](instructions/github/skills/github.skills.instructions.md) (`.github/skills/**`), and [`github.hooks.instructions.md`](instructions/github/hooks/github.hooks.instructions.md) (`.github/hooks/**`).

## File Encoding Rules

**Encoding:** All files must be **UTF-8 without BOM**. Never use UTF-8 with BOM, UTF-16, or any other encoding.

**Line endings:** All `.md` files must use **CRLF** (`\r\n`) line endings. Never write files with LF-only (`\n`) line endings. This is enforced by CI and by `.gitattributes` (`*.md -text`).

**Emojis:** This repository uses Unicode emojis in headings, table cells, and inline markers. Preserve them exactly. Common emojis: headings `🎯 📋 📊 💡 ✅ 🔗 📝 🧭 📂 🔧 🧪 🚀`; table cells `✅ ❌ ⚠️`; arrows `→`.

**When creating or editing files:**
- Write files as UTF-8 without BOM.
- Use CRLF line endings — never LF-only.
- Never re-encode content through lossy pipelines.
- Never strip or replace emoji characters. If a file shows `?` or `??` where emojis should be, that is encoding corruption — restore the original emojis.
