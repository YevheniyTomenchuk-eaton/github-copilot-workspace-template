---
name: pages
description: "Start local GitHub Pages preview server (sets up environment if needed)."
---

# Start Local GitHub Pages Server

Start the Jekyll development server. If the environment is not ready, set it up first.

## Step 1 — Check Environment

Run these checks in a terminal (refresh PATH first):

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
ruby --version
```

If `ruby` is not found → go to **Environment Setup** below, then return here.

If Ruby is found, check if gems are installed:

```powershell
$env:BUNDLE_GEMFILE = "Gemfile.local"
bundle check
```

If `bundle` is not found or gems are not satisfied → run `bundle install` with `BUNDLE_GEMFILE=Gemfile.local`, then continue.

## Step 2 — Start Server

The `Pages: Start Server` task is tracked in `.vscode/tasks.json`, which is the single source of truth for its command, environment, and presentation settings. Always run that task rather than defining a new one inline:

1. Check whether a task labeled `Pages: Start Server` exists in `.vscode/tasks.json`.
2. If it exists, run it with the `run_task` tool (use the existing task ID from the workspace tasks list).
3. If — and only if — the task is missing from `.vscode/tasks.json`, restore it there by copying the canonical definition (including its `options.env.BUNDLE_GEMFILE = "Gemfile.local"`, `presentation`, `problemMatcher`, and `group` fields) from version control, then run it.

Never create a second task with the same label, and never embed a partial copy of the task command in a terminal call — the tracked task definition is the only place the command should live.

The task auto-creates local performance overrides (gitignored theme stubs + asset copies + plugin) and starts the server.

Tell the user the server is starting in the **Pages: Start Server** terminal tab. First-ever build takes ~2 minutes (SCSS compilation + full render). Subsequent starts with cached metadata take ~20 seconds. Incremental rebuilds take ~25 seconds per file change.

The site will be at [http://127.0.0.1:4000/](http://127.0.0.1:4000/). Refresh the browser manually after each rebuild.

## Environment Setup

If Ruby is not installed, guide the user through these steps:

1. Install Ruby 3.2 with DevKit:
   ```powershell
   winget install RubyInstallerTeam.RubyWithDevKit.3.2
   ```
2. Tell the user to complete the GUI installer and run the MSYS2 toolchain setup when prompted (option 3).
3. After installation completes, open a **new terminal** (existing terminals won't see the updated PATH) and install gems:
   ```powershell
   $env:BUNDLE_GEMFILE = "Gemfile.local"
   bundle install
   ```
4. Return to **Step 2** above.

## Notes

- The task auto-creates three gitignored theme overrides (`_includes/css/activation.scss.liquid`, `_layouts/vendor/compress.html`, `assets/js/zzzz-search-data.json`) that replace expensive theme processing with no-op stubs. These do not affect the remote GitHub Pages build.
- Jekyll reuses `.jekyll-metadata` from the previous session to skip unchanged files. If incremental rebuilds seem to rebuild everything, delete `.jekyll-metadata` and restart.
- `Gemfile.local` bundles the theme gem directly instead of downloading it via `jekyll-remote-theme`, which fails behind corporate proxies.
