---
name: fix-corrupted-file
description: "Fix encoding corruption in a file by restoring emojis and special characters replaced with ? or ??."
---

# Fix Corrupted File

Fix encoding corruption in the specified file by restoring emojis and special characters that were replaced with `?` or `??`.

## Corruption Patterns

When files are processed through lossy encoding pipelines, Unicode characters get replaced with literal `?` (U+003F):

| Corrupted | Original | Context |
|-----------|----------|---------|
| `?` (single) | `✅` | Pros/benefits in table cells or bullet lists |
| `?` (single) | `❌` | Cons/drawbacks in table cells |
| `?` (single) | `→` | Arrows between items (e.g., `2?3` → `2→3`) |
| `?` (single) | `←` | Back navigation links |
| `?` (single) | `⚡` | KPI speed metrics |
| `??` (double) | `⚠️` | Warning/medium ratings in comparison tables |
| `??` (double) | `🎯` | Section headings (executive summary, targets) |
| `??` (double) | `📋` | Section headings (problem statement) |
| `??` (double) | `📊` | Section headings (impact analysis, comparisons) |
| `??` (double) | `💡` | Section headings (proposed solution, guidance) |
| `??` (double) | `📝` | Section headings (additional details) |
| `??` (double) | `🔗` | Section headings (references) |
| `??` (double) | `🔧` | KPI tool/reduction metrics |
| `??` (double) | `📂` | Category headings |

## How to Fix

1. **Read the file** and identify lines with `?` or `??` outside of code blocks
2. **Distinguish corruption from legitimate `?`** — question marks in English sentences, URLs (`GetImage?id=123`), C# nullable types (`int?`), and C# null-coalescing (`??`) are NOT corruption
3. **Use git history** as the source of truth: run `git show <commit>:<filepath>` to see the original content with correct emojis
4. **Apply context-based restoration:**
   - `| **Pros** | ? Text` → `| **Pros** | ✅ Text`
   - `| **Cons** | ? Text` → `| **Cons** | ❌ Text`
   - `<br>?` in Pros column → `<br>✅`
   - `<br>?` in Cons column → `<br>❌`
   - `| ? Positive` in comparison tables → `| ✅ Positive`
   - `| ?? Medium` in comparison tables → `| ⚠️ Medium`
   - `- ? Item` in success criteria lists → `- ✅ Item`
   - `## ?? Title` → check git for the correct heading emoji
   - `Word1 ? Word2` (arrows) → `Word1 → Word2`
5. **Write the fixed file** as UTF-8 without BOM

## Important

- Never modify content inside code blocks (``` fenced sections)
- Preserve all existing correct emojis — only fix `?`/`??` that are clearly corruption
- When unsure which emoji a `?` should be, check git history with `git log --all -- <filepath>` and `git show <commit>:<filepath>`
