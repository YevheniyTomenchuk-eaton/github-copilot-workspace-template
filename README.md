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

4. **Customize:** add your own content folders, instructions, prompts, and skills. See [Customization files](workspace/using-copilot/customization-files.md) for the naming and placement rules.

---

## 📚 Learn the Conventions

The conventions are taught in the published **Using Copilot** guide:

- **[Customization files](workspace/using-copilot/customization-files.md)** — the seven building blocks (instructions, prompts, skills, agents, hooks, templates, scripts), folder mirroring, and naming conventions.
- **[Context and commands](workspace/using-copilot/context-and-commands.md)** — how instructions, prompts, skills, and agents fit together.
- **[Tips and tricks](workspace/using-copilot/tips-and-tricks.md)** — small habits that make Copilot faster, cheaper, and smarter.

The always-on global rules and Mermaid diagram standards live in `.github/copilot-instructions.md` and `.github/instructions/` — open them in the repository source. They are intentionally excluded from this published site.

Run `/validate` in Copilot Chat to check your content against all CI rules before shipping, and `/ship` to open a pull request.
