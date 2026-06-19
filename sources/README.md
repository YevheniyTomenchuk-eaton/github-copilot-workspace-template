# `sources/` — Local Reference Material

This folder is a **local scratch space** for reference material you want the AI to read but
**not** publish or commit — source code, data exports, specifications, large documents, or
anything too big or too private to live in the published knowledge base.

## How it works

- Everything you drop in here is **gitignored** — it never gets committed or pushed.
- This `README.md` is the **only** tracked file, so the folder exists right after you clone.
- Jekyll **excludes** this folder, so nothing here is ever published to the site.

## Using it with Copilot

By default, normal searches skip this folder to avoid noise. Ask the AI to look here only
when you need source-level analysis — for example, verifying a fact against real code or data.
When it searches, it includes ignored files and scopes the search to this folder:

- `includeIgnoredFiles: true`
- `includePattern: "sources/**"`

Drop your files in, then point the AI at what you want analyzed.
