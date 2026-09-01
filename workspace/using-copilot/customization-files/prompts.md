---
title: "Prompts — retired, everything is a skill now"
parent: "Customization files"
grand_parent: "Using GitHub Copilot"
nav_order: 2
---

# 🗄️ Prompts — retired

| ← Previous | Next → |
|:---|---:|
| [Instructions](instructions.md) | [Skills](skills.md) |

---

**Prompt files are gone.** There is no `.github/prompts/` folder any more. Every `/command` in this repository is a **[skill](skills.md)**, and every new one is created as a skill too.

Nothing you used to run is lost: **`/ship`**, **`/validate`**, **`/pages`** and the rest are all still there, invoked exactly the same way — by typing **`/name`**.

---

## 🤔 Why prompts were retired

| Reason | What it means for you |
|--------|-----------------------|
| **Same command, nothing to relearn** | A skill is invoked with **`/name`**, exactly as a prompt was |
| **It also fires without a command** | A skill is matched by its **`description`**, so the right one loads even when you *don't* type anything |
| **Several combine in one chat** | The agent loads as many skills as the work needs, one after another, in the **same chat window** — a prompt was one job, one run |
| **Copilot finds them** | Skills are indexed far better than prompt files ever were |
| **The tooling dropped them** | The latest Visual Studio applications **no longer support prompt files at all** |

---

## ➡️ Where to go instead

- **[Skills](skills.md)** — the replacement. That page explains both shapes of a skill: a runnable **`/command`** and **know-how** the AI pulls in on its own.
- **[Instructions](instructions.md)** — for a rule that must *always* hold, applied automatically to every file its `applyTo` matches.
- Ask the AI to **`/create-customization`** and it writes a skill in the right place, with the right name.

> 🧭 **Rule of thumb:** a rule that must always hold → an **instruction**. Something you *do* or *look up* → a **skill**.

> 📝 This page is kept so older links keep working. If you ever find a `.prompt.md` file, it is a leftover — ask the AI to convert it into a skill.

---

| ← Previous | Next → |
|:---|---:|
| [Instructions](instructions.md) | [Skills](skills.md) |
