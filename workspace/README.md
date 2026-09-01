---
title: "Workspace"
nav_order: 9
has_toc: false
---

# 🧰 Workspace

Everything you need to **work with this repository using GitHub Copilot Chat** — the skills, agents, instructions, and hooks that turn it into an automated workspace.

> 🆕 **New to GitHub Copilot in VS Code?** Start with the **[Using GitHub Copilot](using-copilot/README.md)** guide — a short, picture-led walkthrough of agents, models, approvals, context, and costs. No prior experience needed.

> ⚡ In a hurry? Jump straight to the **[Cheatsheet](using-copilot/cheatsheet.md)**.

## 🚀 Start here

1. Open this repository in VS Code (`code .`). Copilot picks up the `.github/` customization folders automatically.
2. Open Copilot Chat, switch to **Agent** mode, and try a skill — type `/` to see the available slash commands.
3. Preview the published site locally with `/pages` whenever you want to see your changes rendered.

## 🧩 How the pieces fit together

| Piece | What it is | Where it lives |
|-------|-----------|----------------|
| **Skills** | Named workflows you invoke with `/<name>`, and reusable domain know-how an agent loads on demand | `.github/skills/` |
| **Agents** | Specialized chat modes with their own instructions and tools | `.github/agents/` |
| **Instructions** | Rules that auto-apply based on the file you are editing | `.github/instructions/` |
| **Templates** | Structural skeletons new files are copied from | `.github/templates/` |
| **Scripts** | Validation and helper scripts the skills run (e.g. `/validate`) | `.github/scripts/` |
| **Hooks** | Your own code that runs automatically on a chat lifecycle event | `.github/hooks/` |
| **Workflows** | GitHub Actions that re-run the same checks on every PR | `.github/workflows/` |
| **Sources** | Local-only reference material the AI can read but never publishes | `sources/` |

You type a **`/command`** or pick an **agent**; they pull in the right **skills**, **instructions**, and **templates** automatically. **Scripts** and **workflows** keep your work valid — `/validate` runs the scripts locally, and the workflows re-run them on every PR.

The [Toolkit](../toolkit/README.md) holds the Office document generators (deck, workbook, document, email). This page covers the **workspace-wide** skills and the building blocks they use.

---

## ⚡ Workspace Skills

Workspace-wide skills that work anywhere in the repository. Invoke each with `/<name>` and describe what you need — or just describe the job, and the agent loads the matching skill by itself.

### Authoring & shipping

| Skill | What it does |
|-------|--------------|
| `/validate` | Run all CI validation checks locally (front matter, links, tables, diagrams, encoding) before shipping |
| `/ship` | Commit, push, and open a pull request — never commits to `main` directly |
| `/latest` | Switch to `main` and pull the latest commits — refuses to switch with uncommitted work |
| `/update-branch` | Merge the latest base branch into the current feature branch and resolve conflicts — like GitHub's Update branch button |
| `/pages` | Start the local GitHub Pages preview server (sets up Ruby + Bundler if needed) |
| `/fix-corrupted-file` | Restore emojis and special characters that got replaced with `?` or `??` (encoding corruption) |
| `/create-customization` | Scaffold a new `.github/` customization file (instruction, skill, agent, template, script, or hook) in the right place with the right name |

### Maintenance

| Skill | What it does |
|-------|--------------|
| `/clean-memory` | Delete all AI memory files — enforces the policy that persistent knowledge lives in `.github/instructions/` |

### Reviewing

| Skill | What it does |
|-------|--------------|
| `/fix-cr` | One pass: resolve open review comments from every reviewer (human and Copilot), fix already-failed CI checks, reply, and request a fresh Copilot review |
| `/fix-cr-autopilot` | Unattended loop: fix review comments → push → request Copilot re-review → wait → repeat until the CR is clean |

---

## 🧠 Knowledge skills

Same building block, other shape: these carry no workflow of their own — they are the **know-how** an agent loads the moment your task matches their description.

| Skill | What it covers |
|-------|----------------|
| `github` | `gh` CLI and API — PR workflows, review threads, CI checks, Copilot re-review |
| `github-conventions` | How to choose and name customization files under `.github/` |
| `office-documents` | Brand system and JSON spec schemas for the Office document generators (deck, workbook, document, email) |
| `sharepoint-upload` | Upload a local file or folder to any SharePoint folder you name at run time |

Add your own skills for any domain knowledge you want agents to load on demand — see the [`github-conventions`](../.github/skills/github-conventions/SKILL.md) skill for the decision matrix.

---

## 🎭 Agents

| Agent | Use for |
|-------|---------|
| `general` | Any task — writing, research, terminal commands — with awareness of this workspace's conventions |
| `toolkit` | Producing on-brand Office files — a deck, workbook, document, or email draft |

Pick an agent when a whole task fits its expertise; it brings its own instructions, skills, and tools. Define new agents under `.github/agents/` for specialized workflows.
