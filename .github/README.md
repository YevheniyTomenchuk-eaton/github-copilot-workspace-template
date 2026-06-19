# GitHub Copilot Workspace Template — Framework Guide

Developer guide for cloning, setting up, and customizing this AI-powered workspace.

---

## What Is This?

A **template** for building your own GitHub Copilot-powered workspace. It pairs two things:

1. A **GitHub Pages** site (Jekyll + [just-the-docs](https://just-the-docs.com/README.md)) — any Markdown you add is published as a searchable documentation site.
2. An **AI framework** under `.github/` — instructions, prompts, agents, skills, templates, scripts, and hooks that teach Copilot your conventions and automate repeatable tasks.

Clone it, open it in VS Code, keep what helps, and delete what you don't need. The `toolkit/` examples (email, presentation, excel, word) demonstrate the end-to-end pattern: a prompt that calls a script and fills a template, governed by an instruction file.

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
```

### 2. Open in VS Code

```bash
code .
```

The workspace is pre-configured in `.vscode/settings.json`:

```json
{
  "chat.promptFilesLocations": {
    ".github/prompts": true,
    ".github/prompts/**": true
  },
  "chat.instructionsFilesLocations": {
    ".github/instructions": true,
    ".github/instructions/**": true
  },
  "chat.agentFilesLocations": {
    ".github/agents": true
  },
  "chat.agentSkillsLocations": {
    ".github/skills": true
  },
  "chat.hookFilesLocations": {
    ".github/hooks": true
  }
}
```

This enables AI instructions, prompts, agents, skills, and hooks automatically. No extra setup needed.

### 3. Run the site locally (optional)

Preview the GitHub Pages site on your machine before pushing changes. Type `/pages` in Copilot Chat — it handles environment setup and server startup automatically.

**Manual alternative:** Install Ruby 3.1+ with DevKit (`winget install RubyInstallerTeam.RubyWithDevKit.3.2`), open a new terminal, run `$env:BUNDLE_GEMFILE = "Gemfile.local"; bundle install`, then use the VS Code task **Pages: Start Server** (Terminal → Run Task).

Site opens at [http://127.0.0.1:4000/](http://127.0.0.1:4000/). First-ever build typically takes about 1–2 minutes. Subsequent starts are usually about 15–20 seconds.

> **Why `Gemfile.local`?** The production `Gemfile` uses `jekyll-remote-theme` which downloads the theme from GitHub at build time. Behind corporate proxies this fails with SSL errors. `Gemfile.local` bundles the theme gem directly.

### 4. Optional tooling for the toolkit examples

The `toolkit/` examples generate Office documents. To run them, install the Python packages they use:

```bash
pip install python-pptx openpyxl python-docx
```

For the GitHub helper scripts (PR review, CI checks), install and authenticate the GitHub CLI:

```bash
gh auth login
```

### 5. Set up the `sources/` folder (optional)

The optional `sources/` folder is a local, gitignored place to drop **reference material you want the AI to read** — source code, data exports, specs, large documents, anything too big or too private to publish. It is gitignored and excluded from Jekyll, so nothing in it is committed or appears on the site. Create it whenever you have material the AI should analyze:

```
sources/
└── <whatever you want the AI to read>
```

The AI searches it only on request — use `grep_search` with `includeIgnoredFiles: true` and `includePattern: "sources/**"`. Regular content editing does not need it.

---

## Repository Structure

| Folder | Description | Published |
|--------|-------------|-----------|
| `workspace/` | Onboarding guide — how to use Copilot in this workspace | ✅ |
| `toolkit/` | Worked examples that generate Office documents — gitignored outputs | ✅ |
| `organization/` | Placeholder example — document people, sites, roles, and teams as a single source of truth | ✅ |
| `sources/` | Optional local reference material for AI analysis — gitignored, never published | ❌ |
| `.github/` | AI instructions, prompts, templates, agents, skills, scripts, and hooks | ❌ |

Add your own top-level folders for whatever content you want to publish — each becomes a section in the site sidebar.

---

## AI Framework

### Core Principle: Single Source of Truth

If a value has a canonical definition file, **link to it** instead of repeating it as plain text. Plain text drifts silently; links stay consistent. This pattern is optional — adopt it where it helps.

### Hierarchical Instruction Model

The AI framework uses a **waterfall** of layers. Each adds more specific context on top of the previous one:

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Global Instructions                   │
│  .github/copilot-instructions.md                │
│  Always loaded. Repository rules, naming,        │
│  encoding, navigation, conventions.              │
├─────────────────────────────────────────────────┤
│  Layer 2: Contextual Instructions               │
│  .github/instructions/{domain}/                 │
│  Auto-loaded when working in matching folders.   │
│  Domain-specific rules stack hierarchically.     │
├─────────────────────────────────────────────────┤
│  Layer 3: Prompts                               │
│  .github/prompts/{domain}/                      │
│  Manually invoked slash commands.                │
│  Each prompt links to templates and scripts.     │
├─────────────────────────────────────────────────┤
│  Layer 4: Agents                                │
│  .github/agents/{name}.agent.md                 │
│  Custom agent modes with specialized behavior.   │
├─────────────────────────────────────────────────┤
│  Layer 5: Skills                                │
│  .github/skills/{name}/SKILL.md                 │
│  Reusable domain knowledge packages.             │
│  Auto-invoked when agent detects matching task.  │
└─────────────────────────────────────────────────┘
```

**Layer 1 — Global instructions** (`copilot-instructions.md`): Loaded into every Copilot conversation automatically. Defines universal rules for naming, diagrams, encoding, navigation, and the `.github/` conventions.

**Layer 2 — Contextual instructions** (`instructions/`): Loaded automatically based on which file you're editing. The `applyTo` frontmatter controls activation:

```yaml
---
applyTo: "toolkit/**"
---
```

Instructions stack hierarchically. Editing a file in `toolkit/email/` loads the global instructions plus every instruction whose `applyTo` glob matches that path. Each level adds rules without repeating what the parent already defined.

**Layer 3 — Prompts** (`prompts/`): Slash commands invoked manually (e.g., `/validate`, `/ship`). Each prompt links to template files and scripts, forcing the AI to use real, deterministic logic before generating anything.

**Layer 4 — Agents** (`agents/`): Custom agent modes that specialize the AI for different contexts. Switch with `@agent-name` in chat. This template ships one agent, `@general`, aware of the workspace conventions. Add your own.

**Layer 5 — Skills** (`skills/`): Reusable domain knowledge packages that agents invoke automatically when they detect a matching task. Each skill lives in its own subfolder with a `SKILL.md` file containing step-by-step instructions, checklists, and reference examples.

### Hooks

Hooks live in `.github/hooks/` as JSON files that bind a VS Code chat lifecycle event (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and so on) to a command — always a **script** under `.github/scripts/`, never inlined logic. Filenames use the same dot-path mirroring as the other artifacts but sit **flat** in `.github/hooks/` (the loader is single-level per folder). The flat folder is registered by default; a deliberately nested subfolder needs its own `chat.hookFilesLocations` entry in `.vscode/settings.json`. See [`github.hooks.instructions.md`](instructions/github/hooks/github.hooks.instructions.md) and the [hooks tour demo](../workspace/demo/README.md).

### Templates

Templates live in `.github/templates/` and mirror the project structure. Each instruction file links to its relevant template(s). The AI uses the template as a structural skeleton when generating new content. Templates never live in project folders — only in `.github/templates/`.

### How They Connect

```
Agent ──uses──► Skill (auto-invoked for matching tasks)
  │
  └──uses──► Prompt ──references──► Instruction ──references──► Template
               │                        │                          │
               │                        │                          └─ Structural skeleton
               │                        └─ Domain rules, checklists, quality gates
               └─ Entry point (slash command the user invokes)
```

When you invoke a prompt:
1. The prompt tells the AI what to do and links to the instruction file.
2. The instruction file defines rules, quality checks, and links to the template.
3. The AI reads the template, fills it in following the rules, and calls any scripts for deterministic logic.

### Folder Mirroring

Both `instructions/` and `prompts/` mirror the project folder structure:

```
Project folder   →  Instructions location                  →  Prompts location
toolkit/email/   →  .github/instructions/toolkit/email/    →  .github/prompts/toolkit/email/
toolkit/word/    →  .github/instructions/toolkit/word/     →  .github/prompts/toolkit/word/
```

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Instruction | `{path.to.folder}.instructions.md` | `toolkit.email.instructions.md` |
| Prompt | `{path.to.folder}.{action}.prompt.md` | `toolkit.email.create.prompt.md` |
| Template | `{path.to.folder}.template.{ext}` | `toolkit.email.template.eml` |

### Adding New Domains

1. Create a subdirectory in `instructions/` matching the project folder.
2. Create an `.instructions.md` file with the correct `applyTo` frontmatter.
3. Create a template in `templates/` if the domain produces structured content.
4. Create a prompt in `prompts/` if users need a slash command entry point.

See the [`github-conventions`](skills/github-conventions/SKILL.md) skill for the full decision matrix and naming rules.

---

## `.github/` Directory Structure

```
.github/
├── copilot-instructions.md     # Layer 1 — always-on global rules
├── README.md                   # This file
├── instructions/               # Layer 2 — contextual rules
│   ├── diagram-standards.instructions.md   # Global — Mermaid rules
│   ├── github/                 # How to author .github/ customization files
│   ├── organization/           # Rules for the organization example
│   └── toolkit/                # Rules for the toolkit examples
├── prompts/                    # Layer 3 — slash commands
│   ├── pages.prompt.md             # Start local Jekyll server
│   ├── ship.prompt.md              # Submit changes via PR
│   ├── validate.prompt.md          # Run all CI checks locally
│   ├── fix-corrupted-file.prompt.md
│   └── toolkit/                    # Slash commands for the toolkit examples
├── agents/                     # Layer 4 — custom agent modes
│   └── general.agent.md            # General-purpose, workspace-aware
├── skills/                     # Layer 5 — reusable domain knowledge
│   ├── github/                     # GitHub CLI and API patterns
│   └── github-conventions/         # How to choose and name .github/ files
├── templates/                  # Structural skeletons
│   ├── organization/               # Person page skeleton
│   └── toolkit/
├── scripts/                    # Extracted executable logic
│   ├── check-*.py                  # CI validators
│   ├── check-encoding.ps1
│   ├── github/                     # PR-review and CI helper scripts
│   └── toolkit/                    # Office-document generators
├── hooks/                      # Lifecycle-event automations (JSON, flat)
└── workflows/                  # GitHub Actions CI checks
```
