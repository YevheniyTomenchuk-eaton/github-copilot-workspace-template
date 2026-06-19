---
title: "Workspace"
nav_order: 9
has_toc: false
---

# 🧰 Workspace

Everything you need to **work with this repository using GitHub Copilot Chat** — the prompts, skills, agents, and instructions that turn it into an automated workspace.

> 🆕 **New to GitHub Copilot in VS Code?** Start with the **[Using GitHub Copilot](using-copilot/README.md)** guide — a short, picture-led walkthrough of agents, models, approvals, context, and costs. No prior experience needed.

> ⚡ In a hurry? Jump straight to the **[Cheatsheet](using-copilot/cheatsheet.md)**.

## 🚀 Start here

1. Open this repository in VS Code (`code .`). Copilot picks up the `.github/` customization folders automatically.
2. Open Copilot Chat, switch to **Agent** mode, and try a prompt — type `/` to see the available slash commands.
3. Preview the published site locally with `/pages` whenever you want to see your changes rendered.

## 🧩 How the pieces fit together

| Piece | What it is | Where it lives |
|-------|-----------|----------------|
| **Prompts** | Named workflows you invoke with `/<name>` | `.github/prompts/` |
| **Skills** | Reusable domain know-how a prompt or agent loads on demand | `.github/skills/` |
| **Agents** | Specialized chat modes with their own instructions and tools | `.github/agents/` |
| **Instructions** | Rules that auto-apply based on the file you are editing | `.github/instructions/` |
| **Templates** | Structural skeletons new files are copied from | `.github/templates/` |
| **Scripts** | Validation and helper scripts the prompts run (e.g. `validate`) | `.github/scripts/` |
| **Hooks** | Your own code that runs automatically on a chat lifecycle event | `.github/hooks/` |
| **Workflows** | GitHub Actions that re-run the same checks on every PR | `.github/workflows/` |

You invoke a **prompt** or pick an **agent**; they pull in the right **skills**, **instructions**, and **templates** automatically. **Scripts** and **workflows** keep your work valid — `validate` runs the scripts locally, and the workflows re-run them on every PR.

Worked examples that generate Office documents live in the [Toolkit](../toolkit/README.md). This page covers the **workspace-wide** prompts and the building blocks they use.

---

## ⚡ Workspace Prompts

Workspace-wide prompts that work anywhere in the repository. Invoke each with `/<name>` and describe what you need.

### Authoring & shipping

| Prompt | What it does |
|--------|--------------|
| `validate` | Run all CI validation checks locally (front matter, links, tables, diagrams, encoding) before shipping |
| `ship` | Commit, push, and open a pull request — never commits to `main` directly |
| `latest` | Switch to `main` and pull the latest commits — refuses to switch with uncommitted work |
| `update-branch` | Merge the latest base branch into the current feature branch and resolve conflicts — like GitHub's Update branch button |
| `pages` | Start the local GitHub Pages preview server (sets up Ruby + Bundler if needed) |
| `fix-corrupted-file` | Restore emojis and special characters that got replaced with `?` or `??` (encoding corruption) |
| `create-customization` | Scaffold a new `.github/` customization file (instruction, prompt, agent, skill, template, script, or hook) in the right place with the right name |

### Maintenance

| Prompt | What it does |
|--------|--------------|
| `clean-memory` | Delete all AI memory files — enforces the policy that persistent knowledge lives in `.github/instructions/` |

---

## 🧠 Skills

| Skill | What it covers |
|-------|----------------|
| `github` | `gh` CLI and API — PR workflows, review threads, CI checks, Copilot re-review |
| `github-conventions` | How to choose and name customization files under `.github/` |

Add your own skills for any domain knowledge you want agents to load on demand — see the [`github-conventions`](../.github/skills/github-conventions/SKILL.md) skill for the decision matrix.

---

## 🎭 Agents

| Agent | Use for |
|-------|---------|
| `general` | Any task — writing, research, terminal commands — with awareness of this workspace's conventions |

Pick an agent when a whole task fits its expertise; it brings its own instructions, skills, and tools. Define new agents under `.github/agents/` for specialized workflows.
