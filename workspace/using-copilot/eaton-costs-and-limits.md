---
title: "Eaton costs and limits"
parent: "Using GitHub Copilot"
grand_parent: "Workspace"
nav_order: 12
---

# 💰 Eaton costs and limits

| ← Previous | Next → |
|:---|---:|
| [Tips and tricks](tips-and-tricks.md) | [Cheatsheet](cheatsheet.md) |

---

This page explains how GitHub Copilot is **paid for and limited at Eaton**. The model prices on the [Choosing a model](choosing-a-model.md) page are in **credits**; this page explains what those credits mean for you.

> ⚠️ **Numbers can change.** Eaton updates limits over time. Your **live allowance and usage are always shown inside VS Code** — click the **Copilot icon** in the status bar to confirm the current figures before you rely on them.

---

## How billing works

Copilot usage is billed in **GitHub AI Credits (AIC)**, where **1 credit = $0.01**. Every interaction consumes **tokens**: the text you send (**input**), the AI's reply (**output**), and context it reuses (**cached**). Those tokens are priced by the model you chose and converted into credits.

Two things decide the cost of any interaction:

1. **The model** — a frontier model (Opus 4.8) is priced far higher per token than a light one (GPT-5 mini).
2. **How many tokens** — a quick question costs a fraction of a credit; a long agent session across many files costs much more.

Not all tokens cost the same: **output** is the most expensive (roughly **5×** input), and **cached / reused** text is the cheapest (roughly **10× less** than fresh input). Code completions and inline suggestions are **free** — they are not billed in credits.

| Term | Meaning |
|------|---------|
| **Token** | A small piece of text — about ¾ of a word |
| **AIC** | AI Credits — the unit Copilot usage is billed in. **1 credit = $0.01** |
| **In / Out / Cache** | Tokens you send / the AI generates / reuses. Out is priciest, Cache cheapest |

> 💡 **Rough math:** credits ≈ tokens ÷ 1,000,000 × the model's rate (rates are on the [Choosing a model](choosing-a-model.md) page). With **100 credits = $1**, a short question on a light model is a fraction of a credit, while a long Opus session across many files can run to tens of credits.

---

## Your monthly limit

Your allowance is a pool of **AI credits** that **resets at the start of each month**. At the time of writing it is roughly **100,000 credits (≈ $1,000)** per user, but the **authoritative, live figure is always the one shown in VS Code**.

| Limit | Value |
|-------|-------|
| **Monthly allowance per user** | Shown in VS Code (≈ 100,000 AI credits / $1,000 at time of writing) |
| **Resets** | Start of each month |
| **Need more?** | A special request for a higher limit is possible |

> 💡 Don't rely on the numbers above — they can change. Click the **Copilot icon** in the status bar (bottom-right) to see your real allowance, how much you have used, and when it resets — see [Running and monitoring](running-and-monitoring.md).

---

## 💡 How to stay within budget

The same habits that keep usage low also keep cost low:

- ✅ Use **Auto** or a **cheap model** (GPT-5 mini, Gemini 3.5 Flash) for simple work.
- ✅ Keep context at **200K**, not 1M — a bigger window just lets more billable tokens pile up.
- ✅ Keep reasoning on **High**, not Max, unless needed.
- ✅ Start a **new chat** per task so the memory box stays small.
- ✅ Add **only the files you need** with `#`.
- ❌ Avoid **Opus 4.8 + 1M + Max** for small jobs — that is the most expensive combination.

> A simple edit on a cheap model can cost **10–20× less** than the same edit on the most powerful setup. Match the tool to the task.

---

## Getting access or more capacity

- **Need a Copilot subscription?** Request it through the Eaton DevOps Toolchain Services page:
  [GitHub Enterprise — request access](https://eaton.sharepoint.com/sites/Team_DevOps-Toolchain-Services/SitePages/GitHub-Enterprise.aspx)
  *(One subscription type is available.)*
- **Need a higher monthly limit?** A special request is possible — raise it through the same DevOps Toolchain Services channel.

---

| ← Previous | Next → |
|:---|---:|
| [Tips and tricks](tips-and-tricks.md) | [Cheatsheet](cheatsheet.md) |
