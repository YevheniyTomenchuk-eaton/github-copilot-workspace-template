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

Copilot usage is billed in **GitHub AI Credits (AIC)**, where **1 credit = $0.01**. Every interaction consumes **tokens**: the text you send (**input**), the AI's reply (**output**), and context it reuses (**cached**). Those tokens are priced by the model used and converted into credits.

Two things decide the cost of any interaction:

1. **The model** — a frontier model is priced far higher per token than a light one.
2. **How many tokens** — a quick question costs a fraction of a credit; a long agent session across many files costs much more.

Not all tokens cost the same: **output** is the most expensive (roughly **5×** input), and **cached / reused** text is the cheapest (roughly **10× less** than fresh input). Code completions and inline suggestions are **free** — they are not billed in credits.

| Term | Meaning |
|------|---------|
| **Token** | A small piece of text — about ¾ of a word |
| **AIC** | AI Credits — the unit Copilot usage is billed in. **1 credit = $0.01** |
| **In / Out / Cache** | Tokens you send / the AI generates / reuses. Out is priciest, Cache cheapest |

> 💡 **Rough math:** credits ≈ tokens ÷ 1,000,000 × the model's rate (rates are shown live in **Manage Models**). With **100 credits = $1**, a short question on a light model is a fraction of a credit, while a long flagship session across many files can run to tens of credits.

---

## Your monthly limit

Your allowance is a pool of **AI credits** that **resets at the start of each month**. At the time of writing it is **$300 per user — roughly 30,000 AI credits** — but the **authoritative, live figure is always the one shown in VS Code**.

| Limit | Value |
|-------|-------|
| **Monthly allowance per user** | Shown in VS Code (**$300 ≈ 30,000 AI credits** at time of writing) |
| **Resets** | Start of each month |
| **Need more?** | Possible — but only after you have used **80%** of your allowance, with manager approval and an AI Council session (see below) |

> 💡 Don't rely on the numbers above — they can change. Click the **Copilot icon** in the status bar (bottom-right) to see your real allowance, how much you have used, and when it resets — see [Running and monitoring](running-and-monitoring.md).

---

## 🎟️ Asking for more capacity

Extra capacity is available, but it is **earned rather than requested**. The path has three steps, in order:

| Step | What has to happen |
|---|---|
| **1. Reach 80% usage** | You must have consumed **at least 80% of your monthly allowance** (~24,000 credits / $240 of the $300). Below that threshold the request is not considered — the assumption is that there is still room to work with. |
| **2. Manager approval** | Your manager approves the request for a higher limit. |
| **3. AI Council session** | The request triggers a session with the **AI Council**, where you **present your use case** — what you are automating, what it produces, and why the extra capacity is justified. |

### How to prepare for the AI Council

Treat it as a short demo of value delivered, not a plea for budget. What lands well:

- **What you automated** — the concrete processes now running through AI, ideally end-to-end rather than one-off chats.
- **What it produced** — work items delivered, documentation generated, reviews handled, time saved. Real artifacts beat adjectives.
- **Why the credits went where they went** — that the spend is production work, not experimentation.
- **What the extra capacity unlocks** — the specific work you cannot currently finish inside the allowance.

> 💡 The engineers who clear this easily are the ones whose usage is **visible as output**: skills committed to a repo, work items closed, documents generated. If your usage lives only in throwaway chat windows, it is much harder to defend. That is a strong argument for capturing your work as reusable [customization files](customization-files.md).

---

## 💡 How to stay within budget

With a smaller allowance, habits matter more than model choice. The same habits that reduce cost also improve results:

- ✅ Stay on **Auto** — it is **10% cheaper** than picking the same model by hand, and it escalates on its own when the task is genuinely hard.
- ✅ **Plan complex work first** (see [Choosing a model](choosing-a-model.md)). Wrong iterations are the real budget killer — a task described properly the first time can cost a fraction of the same task attempted three times.
- ✅ **Capture repeat work as skills.** A job described once and reused costs a fraction of re-explaining it every time.
- ✅ Keep context at **200K**, not 1M — a bigger window just lets more billable tokens pile up.
- ✅ Keep reasoning on **High**, not Max, unless the task needs it.
- ✅ Start a **new chat** per task so the memory box stays small.
- ✅ Add **only the files you need** with `#`.
- ❌ Avoid a **flagship model + 1M context + Max reasoning** for small jobs — that is the most expensive possible combination.

> A simple edit on a light setup can cost **10–20× less** than the same edit on the most powerful one. Match the tool to the task.

---

## Getting access

- **Need a Copilot subscription?** Request it through the Eaton DevOps Toolchain Services page:
  [GitHub Enterprise — request access](https://eaton.sharepoint.com/sites/Team_DevOps-Toolchain-Services/SitePages/GitHub-Enterprise.aspx)
  *(One subscription type is available.)*
- **Need a higher monthly limit?** Follow the three steps above — 80% usage, manager approval, then the AI Council session.

---

| ← Previous | Next → |
|:---|---:|
| [Tips and tricks](tips-and-tricks.md) | [Cheatsheet](cheatsheet.md) |
