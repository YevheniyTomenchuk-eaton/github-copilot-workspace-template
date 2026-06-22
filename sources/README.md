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

## Recommended: bring source repos in as git submodules

When the reference material is itself a **git repository** (a service, a library, a wiki) and
you want the AI to **index and search it like the rest of the workspace**, add it as a
**git submodule** instead of dropping a plain copy here.

A plain clone or copy under `sources/` is **gitignored**, so VS Code search and Copilot's
workspace index skip it by default — you have to force-include it on every search. A tracked
submodule avoids that:

- **Indexed & searchable** — the submodule's files are tracked, so they show up in normal
  search and indexing with no `includeIgnoredFiles` flag.
- **Pinned & reproducible** — a submodule records an exact commit, so everyone who clones gets
  the same source. Update deliberately with `git submodule update --remote`.
- **Self-describing** — `.gitmodules` is the single map of every source repo and its URL.

### The one catch: the gitignore exception

The blanket `/sources/*` rule in [`.gitignore`](../.gitignore) would also hide a submodule. So
for each submodule you add, **un-ignore its path** so the tracked gitlink survives the rule:

```gitignore
/sources/*
!/sources/README.md
!/sources/my-service        # tracked submodule — keep it indexed
```

Then add the submodule and commit:

```bash
git submodule add <repo-url> sources/my-service
```

> 💡 Want the source present but *not* searchable/indexed? Skip the submodule and just drop a
> copy in — the default `/sources/*` ignore keeps it local-only.
