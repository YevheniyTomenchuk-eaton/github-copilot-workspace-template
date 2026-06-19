---
applyTo: "toolkit/**"
---

# Toolkit — General Instructions

## Writing Style

Every artifact you create must follow these rules:

- **Simple sentences.** One idea per sentence. Short words.
- **Plain language.** Like explaining to someone new. No jargon.
- **Use simple words — always.** Prefer everyday English over fancy or formal words. The reader is reading fast — not an academic.
  - Bad words to avoid (and their simple replacements): _utilize_ → use, _leverage_ → use, _facilitate_ → help, _implement_ → add / build / do, _commence_ → start, _terminate_ → stop / end, _subsequent(ly)_ → next / then / after, _prior to_ → before, _in order to_ → to, _additional_ → more / extra, _approximately_ → about, _demonstrate_ → show, _identify_ → find, _initiate_ → start, _obtain_ → get, _perform_ → do, _provide_ → give / send, _require_ → need, _verify_ → check, _validate_ → check, _ensure_ → make sure, _functionality_ → feature / behavior, _component_ → part, _silently_ → with no message.
  - If a short word fits, use it. If a domain term has no simple alternative, keep the domain term — do not invent unclear synonyms.
- **No filler.** Cut every word that does not add meaning.
- **Be specific.** Use exact names, versions, numbers. Never vague.
- **Structure first.** Bullet points, tables, checklists over paragraphs.
- **Neutral tone.** No ownership language. No emotions. Facts only.
- **No history commentary.** Never write "this was changed from…" or "previously…"

Bad: "It would be beneficial to consider implementing a comprehensive solution for the document generation."
Good: "Add a prompt that builds the document."

## Linking Rules

- **Always link to `README.md`** — never link to a bare folder path. Use `folder/README.md`, not `folder/`.
- Use relative paths between files in the repository.
- Only link to relevant items — do not add links for the sake of linking.

## Output Rules

- Each generated artifact gets its own folder inside its category.
- The default folder naming convention is `YY-MM-DD-HHMM-short-description`.
- Only category `README.md` files are committed. All generated folders are gitignored.
- Never suggest committing generated content.
- Use kebab-case for folder names.
- When generating `.eml` files, always include the `X-Unsent: 1` header so Outlook opens them as editable drafts.

## Toolkit Anatomy

Every toolkit category is registered in **seven** places. Missing any one of them breaks the toolkit (404 on Pages, prompts not discovered, generated files committed by accident, sidebar broken). When you add or rename a toolkit, walk through all seven.

### 1. Published page — `toolkit/{category}/README.md`

The only file tracked in git for the category — and the only one published to Pages. Copy [`toolkit.category-readme.template.md`](../../templates/toolkit/toolkit.category-readme.template.md) as the starting point and fill in the placeholders.

The template's shape is fixed: a one-paragraph purpose, a **Prompts** table (one row per action, including the optional `upload` action), an optional category-specific reference table, then **Sources**, **Outputs**, and **Folder layout**. Drop the `Generator script` and `Upload script` rows only when the category truly has neither.

### 2. Hub registration — `toolkit/README.md`

Add a row to the `## 📂 Categories` table. The link target is `{category}/README.md`. Keep the existing columns:

```markdown
| [{Display Name}]({category}/README.md) | {purpose — what it generates and where it goes} |
```

### 3. Instructions — `.github/instructions/toolkit/{category}/toolkit.{category}.instructions.md`

`applyTo: "toolkit/{category}/**"`. Contains the rules specific to the category (format, naming, output layout, edge cases). Keep it short — defer general rules to this file.

### 4. Prompts — `.github/prompts/toolkit/{category}/toolkit.{category}.{action}.prompt.md`

One file per action. Frontmatter:

```yaml
---
description: "{One-line trigger summary}"
agent: agent
---
```

Body must include: Task, Context Loading (numbered file reads — always include `toolkit.instructions.md` and the category instructions), Action steps, User Input + Example.

### 5. Templates — `.github/templates/toolkit/{category}/` (only if needed)

Static skeletons the prompt copies. File name follows the dot-prefix rule: `toolkit.{category}.{descriptor}.template.{ext}`. The word `template` appears **exactly once**, as the suffix.

### 6. Git tracking — `.gitignore`

Add the category's generated outputs to the toolkit block. The default shape ignores everything but the README:

```gitignore
toolkit/{category}/*
!toolkit/{category}/README.md
```

When outputs are single files of a known extension, mirror the existing per-extension lines instead:

```gitignore
toolkit/{category}/*.{ext}
```

### 7. Jekyll exclusion — `_config.yml` **and** `_config_local.yml`

`.gitignore` is invisible to Jekyll. Without an explicit `exclude:` entry, Jekyll still scans every gitignored sub-folder, bloats `_site/`, and breaks incremental rebuilds (the category README stops being emitted). Add patterns that match what the toolkit produces, in **both** files:

```yaml
- toolkit/{category}/*.{ext}          # one line per single-file extension
- toolkit/{category}/*/               # all per-run subfolders (timestamped)
```

Add one `*.{ext}` line per output extension the toolkit produces. Avoid brace-style multi-extension globs — they are not used elsewhere in the config. After editing config, delete `.jekyll-cache/` and `.jekyll-metadata` so the next server start is a full rebuild.

### Edge cases & gotchas

- **Sidebar parent must match exactly.** `parent: "Toolkit"` matches the `title` of `toolkit/README.md`. Typos break the sidebar silently.
- **Don't link to bare folders.** Always `folder/README.md`, never `folder/` and never `(.)` — kramdown emits a broken anchor.
- **One published file per category.** Never commit anything else under `toolkit/{category}/`.
- **Prompt naming.** Dot-prefix encodes the full path under `prompts/`: `toolkit.{category}.{action}.prompt.md`. No abbreviations, no skipped segments.
- **Custom agents.** If the toolkit needs an agent that does not exist, add it under `.github/agents/{name}.agent.md` and reference it in the prompt frontmatter (`agent: {name}`) and in the README.
