---
title: "Choosing a model"
parent: "Using GitHub Copilot"
grand_parent: "Workspace"
nav_order: 4
---

# 🧠 Choosing a model

| ← Previous | Next → |
|:---|---:|
| [Agents and modes](agents-and-modes.md) | [Thinking and context](thinking-and-context.md) |

---

The **model** is the AI brain. Click the **model** button (#3 on the control bar) to change it.

![Pick a model](assets/04-model-picker.png)

> 🎯 **The most important idea on this page:** find the **balance**. Spend the strong model where it earns its cost, and let a cheaper one handle the rest. The rest of this page teaches you how.

---

## ⭐ The golden rule

> **A smart model writes the recipe. A cheaper one can cook from it.**

Think of the AI in two phases:

- **Building** — creating something new, deep research, anything with lots of pitfalls to weigh, **and writing your reusable building blocks** (skills, prompts, instructions, scripts, templates). This is the *thinking* work. Use the best model (today: **Claude Opus 4.8**) and get it right once.
- **Repeating** — running on top of a setup that is already built. The hard thinking is baked into your building blocks, so a lighter model just follows the recipe. **Auto** is a fine choice here.

The whole point of writing good prompts, skills, and scripts is that the **smart model does the thinking once**, and a cheaper model can repeat it cheaply afterwards. So let the smart model write the recipe — then stop paying flagship prices to reheat it.

See [Eaton costs and limits](eaton-costs-and-limits.md) for your monthly budget. Watch your usage in the status bar — see [Running and monitoring](running-and-monitoring.md).

---

## 🎯 The rule of thumb

Three simple buckets:

| Your task | Model |
|-----------|-------|
| **Building new stuff** — new features, deep research, tricky pitfall-heavy work, or authoring your prompts / skills / instructions / scripts / templates | **Opus 4.8** — the flagship. Do the thinking once, do it right. |
| **Repeating on a built setup** — the prompts, skills, and scripts are already in place and just need running | **Auto** is fine. The smart model already did the thinking. |
| **Simple, light work** — a short email, moving a file, finding something | **Auto.** No need to spend a flagship on it. |

> 💡 This is not "use Auto everywhere" — it is **balance**. The flagship builds; the cheaper model repeats. Pick whichever phase you are in.

---

## 🤖 More about "Auto"

**Auto** lets VS Code pick the model, and it is **10% cheaper**. It is the right tool for the *repeating* and *simple* buckets above — but know its limits before you reach for it while **building**:

- Auto **leans toward lighter, older, cheaper** models. It rarely picks a heavy one.
- On open-ended or tricky work, lighter models often need **several tries** — you send a prompt, the answer is not quite right, you correct it, repeat. This **ping-pong** burns prompts and time.
- A **strong** model with one good prompt often finishes that same hard task in one go.

So Auto shines once the thinking is already done — and a flagship earns its cost while the thinking is still happening:

| Use Auto when… | Use the flagship (Opus 4.8) when… |
|----------------|-----------------------------------|
| Daily, repeatable tasks | Development, QA, research, building something new |
| Good instructions, prompts, agents, and skills already guide it | Those building blocks don't exist yet — you are writing them |
| The work is simple — a quick edit, email, or lookup | The task is open-ended or full of pitfalls |

> 💡 Auto is not bad — with strong instructions and prompts it is fine for everyday work. But for real building, pick the latest flagship and get it done in one iteration.

---

## 🧹 How to know which models still make sense

There are **many** models in the list. Most are **redundant**. Here is the mindset to cut the list down — apply it whenever new models appear.

Cost is shown in **credits per 1 million tokens**, split into **In / Out / Cache** (your prompt / the AI reply / reused text). A token is about ¾ of a word, **1 credit = $0.01**, and **Out is the priciest** column — usually about **5×** the In rate, while reused **Cache** text is the cheapest.

### Rule 1 — Same price, older version → drop the older

| Model | Context | In / Out / Cache |
|-------|---------|------------------|
| Claude Opus 4.5 | 200K | 500 / 2500 / 50 |
| Claude Opus 4.6 | 1M | 500 / 2500 / 50 |
| Claude Opus 4.7 | 1M | 500 / 2500 / 50 |
| **Claude Opus 4.8** ✅ | 1M | 500 / 2500 / 50 |

Opus 4.5, 4.6, and 4.7 cost **exactly the same** as 4.8. The newest is the smartest at the same price, so the older ones make **no sense** — keep only **4.8**.

### Rule 2 — Less for the same price → drop it

| Model | Context | In / Out / Cache |
|-------|---------|------------------|
| Claude Sonnet 4.5 | 200K | 300 / 1500 / 30 |
| **Claude Sonnet 4.6** ✅ | 1M | 300 / 1500 / 30 |

Same price, but 4.6 has **5× the memory**. Sonnet 4.5 is strictly worse — drop it.

### Rule 3 — Pricier overlap → drop the dearer one for that job

| Model | Context | In / Out / Cache | Verdict |
|-------|---------|------------------|---------|
| **GPT-5 mini** ✅ | 192K | 25 / 200 / 2.5 | Cheapest — keep as the budget option |
| GPT-5.4 mini | 400K | 75 / 450 / 7.5 | ~3× the price for a "mini" — drop |
| GPT-5.5 | 1M | 500 / 3000 / 50 | Costs like Opus 4.8, but Opus is your hard-task pick — drop |
| Claude Haiku 4.5 | 200K | 100 / 500 / 10 | Cheap, but GPT-5 mini is cheaper — drop |

For each **job** there is already a better-value model. The dearer overlaps add nothing.

### Rule 4 — One model per job is enough

Keep the **best at each role**, hide the rest. That leaves a short, clear list.

---

## ✅ The five models worth keeping

| Model | Role | Memory | In / Out / Cache |
|-------|------|--------|------------------|
| **Claude Opus 4.8** | Top brain — hardest tasks, big builds | 1M | 500 / 2500 / 50 |
| **Claude Sonnet 4.6** | Balanced daily work | 1M | 300 / 1500 / 30 |
| **GPT-5.3-Codex** | Pure coding | 400K | 175 / 1400 / 17.5 |
| **Gemini 3.5 Flash** | Fast + cheap, big memory | 1M | 150 / 900 / 15 |
| **GPT-5 mini** | Cheapest — simple edits | 192K | 25 / 200 / 2.5 |

Turn models on and off with the **eye icon** in **Manage Models**:

![Manage models table](assets/09-manage-models.png)

- The **eye icon** shows or hides a model in your picker.
- The **cost columns** show credits per 1M tokens (In / Out / Cache).
- **Add Models…** enables more brains.

---

## 👥 Matching model to phase

| You are… | Do this |
|----------|---------|
| **Building** — new work, deep research, or writing prompts/skills/scripts | Use **Opus 4.8**. The thinking happens here; make it count. |
| **Repeating** — running a setup that is already built | **Auto** is fine, and 10% cheaper. |
| **Doing something simple** — a quick edit, email, or lookup | **Auto**, or a cheap fast model. |

### Want to stretch your budget further?

- Use **GPT-5 mini** or **Gemini 3.5 Flash** for simple edits and questions.
- Use **Sonnet 4.6** or **GPT-5.3-Codex** for normal coding.
- Keep **Opus 4.8** for the genuinely hard work and for building your blocks.
- Keep context at **200K** and reasoning on **High** unless you need more — see [Thinking and context](thinking-and-context.md).

> ⚠️ The most expensive combo is **Opus 4.8 + 1M context + Max reasoning**. Worth it for a hard problem; wasteful for a one-line change.

---

| ← Previous | Next → |
|:---|---:|
| [Agents and modes](agents-and-modes.md) | [Thinking and context](thinking-and-context.md) |
