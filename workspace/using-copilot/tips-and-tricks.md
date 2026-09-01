---
title: "Tips and tricks (lifehacks)"
parent: "Using GitHub Copilot"
grand_parent: "Workspace"
nav_order: 11
---

# 💡 Tips and tricks (lifehacks)

| ← Previous | Next → |
|:---|---:|
| [Recommended settings](recommended-settings.md) | [Eaton costs and limits](eaton-costs-and-limits.md) |

---

Small habits that make Copilot faster, cheaper, and smarter. Each one is a single idea — skim the list, steal what you like.

---

## 🧹 1. One task = one new chat

Start a **fresh chat** (chat panel chevron → *New Chat Editor*) for every new task.

A fresh chat has **empty memory**, so the AI is not confused by old, unrelated work — and you are not paying to re-read it. When a task is done, open a new one.

> ❌ Don't keep one giant chat open for days. ✅ New task, new chat.

---

## 📎 2. Add only the context you need

Use **`#`** to attach the exact file, folder, or skill the task needs — nothing more.

More files = a fuller memory box = higher cost and a more distracted AI. Precise context gives sharper answers.

> 🎯 **You are the only real limit.** With the right model, clear instructions, and all the needed context, the AI can implement *almost anything*. If you describe the task clearly, provide what it needs, and state exactly what you want — it will usually get there. Vague in, vague out; clear in, done.

---

## 📜 3. Turn repetitive work into a script

This is the big **token-saver**. If a job is **mechanical and repeats** — rename files, regenerate a spreadsheet, check every link — don't make the AI re-think it each time.

1. Ask once: *"write a script that does this."*
2. After that, just **run the script**. Fast, cheap, identical every run.

> 🧠 Save the AI's "thinking" for decisions. Hand the boring, deterministic steps to a script. See [Customization files](customization-files.md).

---

## 📐 4. Template the things you repeat

If you keep creating the **same kind of file** — a gap, a report, a PBI — ask the AI to **make a template** out of one good example. Next time it copies the template instead of inventing the structure again.

Templates keep every result **consistent** *and* **save tokens** — the AI fills in the blanks instead of re-deciding the whole shape each time.

> 🧩 Spot something repeatable? Say *"turn this into a template and reuse it next time."* See [Customization files](customization-files.md).

> 💰 Together, **scripts + templates** are your two biggest token-savers: scripts replace repeated *thinking*, templates replace repeated *structure*.

---

## 💾 5. When something works, ask the AI to save it

Got a workflow, rule, or piece of know-how that worked well? Ask the AI to **capture it**:

- *"Turn this into a skill"* → reusable `/command`
- *"Save these as an instruction"* → auto-applied rules
- *"Make a skill out of this"* → on-demand know-how the AI pulls in by itself

Next time, it just works — you don't re-explain it. (See [Customization files](customization-files.md).)

---

## 🔎 6. Name skills area-first, in kebab-case

You don't have to **memorize** command names. Every skill in this repo is named in **kebab-case**, **area first and action last** — so typing `/` plus a few letters narrows the list to exactly the family you want.

That's why our skills are called things like `toolkit-email-create` and `toolkit-word-upload` — the name *is* the location plus the job. Type `/toolkit` and every toolkit command is right there, self-labelled.

> 🏷️ When you save a new skill, name it the same way: `area-thing-action`, all lowercase, hyphens between words. Future-you will find it instantly.

---

## 🧠 7. Match the model to the job

Find the **balance** — a smart model writes the recipe, a cheaper one cooks from it:

- **Building new stuff / deep research / writing skills & scripts** → the flagship (Opus 4.8). Do the thinking once, do it right.
- **Repeating a setup that is already built** → **Auto** is fine — the hard thinking is baked in.
- **Simple, light work** (short email, move a file, find something) → **Auto**, or a cheap fast model (Flash, mini).

The flagship builds; a cheaper model repeats. See [Choosing a model](choosing-a-model.md).

---

## 🎚️ 8. Dial reasoning up only when needed

Leave **reasoning effort** on **High**. Only push to *Xhigh / Max* when the AI keeps getting a hard problem wrong — higher effort is slower and costs more. (See [Thinking and context](thinking-and-context.md).)

---

## ✅ 9. Stop the approval pop-ups (once you trust it)

Tired of clicking *Allow*? Turn on auto-approve so the agent runs tools without asking — while still pausing to ask **you** real questions.

```jsonc
"chat.tools.global.autoApprove": true
```

> ⚠️ Do this only when your work is in **Git** (so anything can be undone). Prefer approving just safe commands while learning. See [Recommended settings](recommended-settings.md).

---

## ♾️ 10. Never let it stop mid-task

Set the **max requests** setting to a huge number so the agent finishes a whole job without pausing to ask *"keep going?"*.

```jsonc
"chat.agent.maxRequests": 1000000000
```

---

## 🗣️ 11. Steer instead of restarting

The agent went the wrong way? **Don't stop and start over.** Type a correction while it runs and pick **Steer** — it changes direction and keeps the context. (See [Running and monitoring](running-and-monitoring.md).)

---

## 🧵 12. Run many chats in parallel

Open several **chat editors** as tabs and start a task in each. They run **at the same time**.

> 👷 Think of it like managing a small team: you hand out work and orchestrate — you don't do every step yourself.

---

## 📐 13. Ask for a plan first on big tasks

For anything large or risky, switch to **Plan** mode (or just say *"make a plan first, don't change anything yet"*). Review the plan, then let it run. Cheaper than letting it charge off in the wrong direction.

---

## 🔄 14. Let it compact automatically

When the memory box fills, VS Code **compacts it for you** — you rarely need to touch the *Compact Conversation* button. If the AI starts forgetting, a **new chat** is the better fix. (See [Thinking and context](thinking-and-context.md).)

---

## 👀 15. Keep an eye on usage

Click the **Copilot icon** in the status bar to see credits used and when they reset. A quick glance now and then avoids surprises. (See [Eaton costs and limits](eaton-costs-and-limits.md).)

---

## 🔗 16. Add searchable source as a git submodule

Want the AI to **search and index an external codebase**? Don't drop a plain copy into `sources/` — that folder is **gitignored**, so VS Code search and Copilot's index skip it by default (you'd have to force-include it every time).

Instead, add the repo as a **git submodule**. A tracked submodule is:

- **Indexed and searchable** like the rest of the workspace — no `includeIgnoredFiles` needed,
- **Pinned to an exact commit**, so everyone clones the same source,
- **Updated on demand** with `git submodule update --remote`.

> ⚠️ **One catch:** the default `/sources/*` rule in `.gitignore` would hide the submodule too. Un-ignore its path (`!/sources/my-repo`) so the tracked submodule survives. The `sources/` README spells out the full pattern.

---

> ✅ **The one-line summary:** start fresh, give precise context, script and template the repetitive stuff, save what works, and match the model and effort to the task.

---

| ← Previous | Next → |
|:---|---:|
| [Recommended settings](recommended-settings.md) | [Eaton costs and limits](eaton-costs-and-limits.md) |
