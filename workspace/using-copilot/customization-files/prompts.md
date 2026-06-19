---
title: "Prompts — saved workflows you run with /"
parent: "Customization files"
grand_parent: "Using GitHub Copilot"
nav_order: 2
---

# 2️⃣ Prompts — saved workflows you run with /

| ← Previous | Next → |
|:---|---:|
| [Instructions](instructions.md) | [Skills](skills.md) |

---

A **prompt** is a multi-step job captured once so anyone can repeat it perfectly. You run it by typing **`/name`** in the chat box. Where an instruction is *ambient*, a prompt is *deliberate* — nothing happens until you call it.

The key property is **`description`** — it tells both you and the AI what the prompt is for, and it is how VS Code decides to suggest the prompt when you type `/`.

```yaml
---
description: "Run all CI validation checks locally. Use when the user
says 'validate' or wants to check for errors before shipping."
agent: agent
---
# Validate — Run All CI Checks Locally
Run each script below sequentially, then present a summary…
```

---

## 🧩 What's inside a prompt

| Part | Job |
|------|-----|
| **`description`** | When to suggest it; the "elevator pitch" the AI matches against |
| **`agent`** | Which agent the command runs under — `agent` for the default, or a named one like `general` |
| **body** | Plain-Markdown instructions written **for the AI** — the steps to perform |
| **`argument-hint`** *(optional)* | Hints the values the prompt expects when you run it |

The body is just clear instructions. A good prompt reads like a checklist a careful colleague would follow.

---

## ▶️ How you run one

1. Type **`/`** in the chat box — VS Code lists available prompts.
2. Pick one (or keep typing its name), add any arguments, and send.
3. The AI executes the body step by step, asking for approval where needed.

> 💡 Prompts in this repo: **`/ship`** (branch, commit, push, open a PR), **`/validate`** (run all checks), **`/pages`** (start the local preview). Each lives in `.github/prompts/` with a name like `create-customization.prompt.md`.

---

## 🚫 Keep prompts declarative

A prompt should **describe the work and call scripts** — never paste a script's contents inside itself. If a prompt needs to run real logic, it points at a [script](scripts.md); if it tells the AI to create a file, it points at a [template](templates.md). This is the [golden rule](../customization-files.md#golden-rule): one job, one home.

---

## 🧭 Prompt vs the others

| Use a prompt when… | Use something else when… |
|--------------------|--------------------------|
| You repeat a **multi-step job** and want one command | The rule should always apply silently → [Instruction](instructions.md) |
| The steps need **AI judgement** each run | The steps are purely mechanical → [Script](scripts.md) |
| You want it **on demand**, by name | You want a whole **persona + toolset** → [Agent](agents.md) |

---

| ← Previous | Next → |
|:---|---:|
| [Instructions](instructions.md) | [Skills](skills.md) |
