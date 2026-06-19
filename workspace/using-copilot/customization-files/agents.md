---
title: "Agents — expert modes with their own rules"
parent: "Customization files"
grand_parent: "Using GitHub Copilot"
nav_order: 4
---

# 4️⃣ Agents — expert modes with their own rules

| ← Previous | Next → |
|:---|---:|
| [Skills](skills.md) | [Hooks](hooks.md) |

---

An **agent** is a whole **chat mode** built for one kind of work. It has its own system instructions, its own allowed tools, and often a preferred model. You pick it from the **mode menu** on the chat control bar (see [Agents and modes](../agents-and-modes.md)). Picking an agent is like choosing the right specialist for the job — it already knows our conventions.

```yaml
---
name: general
description: "General-purpose assistant with full awareness of this
repository's structure and conventions. Use for any task — authoring,
research, or running the workspace prompts."
model: [claude-opus-4.6, claude-sonnet-4]
---
# General Agent
You help with any task in this repository, following its conventions…
```

---

## 🧩 What defines an agent

| Property | Job |
|----------|-----|
| **`name`** | What appears in the mode menu |
| **`description`** | What the agent specializes in (also used when one agent calls another) |
| **`model`** | Preferred model(s) for this work |
| **body** | The agent's personality, rules, and workflow |

---

## 🤝 Agents can call other agents (subagents)

An agent can hand a focused job to a **subagent** — a fresh, context-isolated helper — and read back only its result. This keeps the main chat clean and lets a specialist do one slice of work. In this repo the built-in **Explore** subagent is used for fast read-only codebase questions while the main agent keeps working.

> 💡 **Trick:** delegating to a subagent is also a *token* win — the subagent's noisy intermediate steps don't fill your main conversation; you get just the summary back.

---

## 🧰 Agents in this template

| Agent | For |
|-------|-----|
| `general` | Any task, with full awareness of this repo's structure and conventions |
| `Explore` *(built-in)* | Fast, read-only codebase exploration delegated by another agent |

This template ships a single ready-made `general` agent so you have a clean starting point. Add your own specialists by asking the AI to **`/create-customization`** an agent for the job you have in mind.

> ✅ Pick an agent that matches the **shape** of your task. The agent sets the rules, then loads matching [skills](skills.md) and obeys matching [instructions](instructions.md) on top.

---

## 🧭 Agent vs prompt

A [prompt](prompts.md) is a *single job* you run inside whatever mode you're in. An **agent** is a *persistent persona* — the rules and tools stay in force for the whole conversation, across many prompts and messages.

---

| ← Previous | Next → |
|:---|---:|
| [Skills](skills.md) | [Hooks](hooks.md) |
