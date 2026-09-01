---
title: "Templates — the skeletons new files copy from"
parent: "Customization files"
grand_parent: "Using GitHub Copilot"
nav_order: 6
---

# 5️⃣ Templates — the skeletons new files copy from

| ← Previous | Next → |
|:---|---:|
| [Hooks](hooks.md) | [Scripts](scripts.md) |

---

A **template** is an empty, correctly-structured starting file. When the AI creates a new person record, email, or document, it copies the matching template so the result already has the right headings, front matter, and sections — no two new files drift apart in shape.

Templates live in `.github/templates/`, mirroring the same repository structure as everything else.

---

## 🧩 Why templates exist

| Without a template | With a template |
|--------------------|-----------------|
| Each new file is shaped from memory | Every new file starts from the same skeleton |
| Headings and front matter drift over time | Structure is identical and correct by construction |
| The AI may invent missing sections | The AI fills in known blanks |

> ✅ A template owns the **shape** of a file. The [instruction](instructions.md) or [skill](skills.md) that creates the file owns *when* and *how* to fill it — and links to the template rather than spelling the skeleton out.

---

## 📂 How it works in this repo

When you ask for "a new person in the organization", the AI:

1. Reads the matching instruction (which **links** to the template).
2. Copies the template — e.g. `organization.people.template.md` — as the starting point.
3. Fills in the blanks with your specifics, then registers it in the parent `README.md`.

```mermaid
graph LR
    ASK["You: 'add a new person'"] --> INS["Instruction points<br/>at the template"]
    INS --> TP["Copy organization.people.template.md"]
    TP --> FILL["Fill in the specifics"]
    FILL --> DONE["A correctly-shaped person file"]

    style ASK fill:#2d5f2d,stroke:#51cf66,color:#fff
    style TP fill:#8b5a00,stroke:#ffa94d,color:#fff
    style DONE fill:#2d5f2d,stroke:#51cf66,color:#fff
    style INS fill:#1a4d7a,stroke:#4dabf7,color:#fff
    style FILL fill:#1a4d7a,stroke:#4dabf7,color:#fff
```

> 📝 Templates and instructions live **only** in `.github/`. You never put a `.template.md` next to real content, and you never look for one there.

---

| ← Previous | Next → |
|:---|---:|
| [Hooks](hooks.md) | [Scripts](scripts.md) |
