---
title: "Home"
permalink: /
---

# 🚀 GitHub Copilot Workspace Template

A starting point for building your own GitHub Copilot-powered workspace — teach Copilot your conventions once, then let it do repeatable work for you. Everything you add is also published as a searchable GitHub Pages site.

---

## 🧭 What's Inside

### 🧰 [Workspace](workspace/README.md)

Your onboarding guide — how GitHub Copilot's customization layers (instructions, prompts, agents, skills, hooks) work and how to use them in this workspace.

**Start here:** [Using Copilot →](workspace/README.md)

---

### 🛠️ [Toolkit](toolkit/README.md)

Worked examples that show the full pattern end to end — a prompt that calls a script and fills a template to generate Office documents (email, presentation, spreadsheet, document). Copy these as the model for your own automations.

**Browse:** [Toolkit Examples →](toolkit/README.md)

---

### 🏢 [Organization](organization/README.md)

A placeholder example showing how to document people, sites, roles, and teams as a single source of truth — so toolkits like [Email](toolkit/email/README.md) can link to a person instead of repeating their name and address. Replace the sample data with your own team.

**Browse:** [Organization →](organization/README.md)

---

## 🏁 Getting Started

1. **Clone** this repository and open it in VS Code (`code .`). The `.vscode/settings.json` already points Copilot at the `.github/` customization folders — no extra setup.
2. **Preview the site locally** (optional): run `/pages` in Copilot Chat, or use the **Pages: Start Server** VS Code task. The site opens at [http://127.0.0.1:4000/](http://127.0.0.1:4000/).
3. **Install optional tooling** for the toolkit examples:

   ```bash
   pip install python-pptx openpyxl python-docx
   gh auth login
   ```

4. **Customize:** add your own content folders, instructions, prompts, and skills. See the [`.github/` framework guide](.github/README.md) and the [`github-conventions`](.github/skills/github-conventions/SKILL.md) skill for naming and placement rules.

---

## 📚 Learn the Conventions

- **[`.github/` Framework Guide](.github/README.md)** — the five-layer instruction model, folder mirroring, and naming conventions.
- **[copilot-instructions.md](.github/copilot-instructions.md)** — the always-on global rules (naming, encoding, diagrams, navigation, git workflow).
- **[Diagram Standards](.github/instructions/diagram-standards.instructions.md)** — the Mermaid palette and size limits enforced by CI.

Run `/validate` in Copilot Chat to check your content against all CI rules before shipping, and `/ship` to open a pull request.
