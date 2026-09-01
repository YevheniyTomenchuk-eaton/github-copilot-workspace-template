---
title: "Cheatsheet"
parent: "Using GitHub Copilot"
grand_parent: "Workspace"
nav_order: 13
---

# ⚡ Cheatsheet

| ← Previous | Next → |
|:---|---:|
| [Eaton costs and limits](eaton-costs-and-limits.md) | |

---

Everything on one page. Print it, pin it.

## 🧩 Control bar (bottom of chat)

| Button | Pick | Default |
|--------|------|---------|
| **Mode** | Ask / Plan / Agent / custom agent | Agent |
| **Model** | Auto / a specific brain | Opus 4.8 if budget allows |
| **Reasoning** | Low → Max | High |
| **Context** | 200K / 1M | 200K |
| **Run location** | Local / CLI / Cloud | Local |
| **Approvals** | Default / Bypass / Autopilot | Bypass (once comfortable) |

## 📝 Special keys in the chat box

| Type | Does |
|------|------|
| `#` | Add a file, folder, or skill as context |
| `/` | Run a command (e.g. `/ship`, `/validate`) |

## 🔐 Approval levels

| Level | Meaning |
|-------|---------|
| **Default** | Asks before risky steps — use while learning |
| **Bypass** | Auto-approves every tool, still asks *you* clarifications — **everyday mode** |
| **Autopilot** | Fully autonomous. **Does not stop on its own** to ask for guidance — but an explicit question from a tool or prompt still waits for you |

## 🧠 Model quick pick

> ⭐ **A smart model writes the recipe; a cheaper one cooks from it.** Use **Opus 4.8** to build (new work, research, or your skills/instructions/scripts). Use **Auto** to repeat a built setup or for simple jobs.

| Task | Model |
|------|-------|
| Building new stuff / research / writing skills & scripts | **Opus 4.8** |
| Running a setup that is already built | Auto (10% cheaper) |
| Simple edit, email, find, move | Auto, or GPT-5 mini / Gemini 3.5 Flash |
| Normal coding (saving tokens) | Sonnet 4.6 or GPT-5.3-Codex |
| Hard / big change | Opus 4.8 |

## ✅ Good habits

- One task = **one new chat editor** (chevron → New Chat Editor).
- Add **only the files you need** with `#`.
- **Building something? Use Opus 4.8** — do the thinking once. **Repeating a built setup? Auto is fine.**
- Set **`chat.agent.maxRequests` = 1000000000** so it never stops early.
- Use **Bypass** as your everyday approval mode once comfortable.
- **Watch usage** in the status bar (bottom-right Copilot icon).
- Keep work in **Git** so any change can be undone.

## ❌ Avoid

- One giant chat open for days (memory fills, answers get worse).
- **Auto** for building new stuff or deep research (it picks light models → many tries).
- Opus 4.8 + 1M + Max reasoning for a one-line fix (expensive).
- **Autopilot** before you are comfortable with it **not stopping on its own** to ask for guidance.

## 🆘 Stuck?

| Problem | Fix |
|---------|-----|
| AI forgot earlier steps | Start a **new chat editor** |
| Going the wrong way | Click **Stop**, then steer with a clearer message |
| Too slow / too costly | Switch to a **cheaper model**, drop to **200K** |
| Wrong answer | Add the right file with `#`, raise **reasoning** to High/Max |
| Keeps asking to continue | Set **`chat.agent.maxRequests`** to a huge number |

---

| ← Previous | Next → |
|:---|---:|
| [Eaton costs and limits](eaton-costs-and-limits.md) | |
