---
title: "Ceremonies"
parent: "Organization"
has_toc: false
---

# 🔄 Ceremonies

Recurring team meetings used on the project.

---

## 🏉 Sprint Rules

| Rule | Value |
|------|-------|
| **Duration** | 2 weeks |
| **Starts on** | Monday |
| **Teams** | 2 |

```mermaid
flowchart LR
    D["Daily Standup<br/>(every day)"]
    SP["Sprint Planning<br/>(sprint start)"]
    SR["Sprint Review<br/>(sprint end)"]

    D --> SP
    SP -.->|2-week sprint| SR
    SR -.->|next sprint| SP

    style D fill:#1a4d7a,stroke:#4dabf7,color:#fff
    style SP fill:#1a4d7a,stroke:#4dabf7,color:#fff
    style SR fill:#1a4d7a,stroke:#4dabf7,color:#fff
```

---

## 📋 Ceremony Overview

| Ceremony | Cadence | Duration | Scope |
|----------|---------|----------|-------|
| [Daily Standup](daily-standup/README.md) | Daily | 15 min | Per team |
| [Sprint Planning](sprint-planning/README.md) | Per sprint | 1–2h | All teams |
| [Sprint Review](sprint-review/README.md) | Per sprint | 1h | All teams |
