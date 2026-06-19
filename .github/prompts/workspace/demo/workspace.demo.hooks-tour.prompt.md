---
agent: agent
description: 'Install one temporary hook that wires up every hook event to a single guide script, then trigger each event live in one run — block an action, inject context, chain a subagent, capture an error, and resume after Stop — so a non-technical audience sees what every hook event does. Cleans up afterwards.'
---

# Hooks — The Full Tour

This is the **one demo that shows every hook event** in a single run. A hook can do very different
jobs — **block** an action before it runs, **react** after a tool finishes and chain more work,
**brief** a subagent, **catch** an error, **resume** the agent after it tries to stop. This tour
fires **all of them**, one at a time, and narrates each in plain language so even a non-technical
viewer can follow.

The whole idea in one sentence: **a hook is your own small script that VS Code runs automatically
at a chosen moment** — when a chat starts, before a tool runs, after it finishes, when an error
happens, when the agent tries to stop, and so on. This tour makes each of those moments happen on
purpose and shows what a hook can do at each one.

> 🪝 **One script backs the whole tour.** Every event points at the same committed guide script,
> [`.github/scripts/workspace/demo/hook-tour.ps1`](../../../scripts/workspace/demo/hook-tour.ps1),
> which is given the event name with `-Event`. The script is **inert unless the tour is armed**
> (a marker folder in TEMP), so it can never touch real work. The logic lives in the script — the
> hook only points at it, exactly as the golden rule requires.

## ⚠️ What this demo touches (and cleans up)

This prompt **creates one temporary hook file** at `.github/hooks/workspace.demo.hooks-tour.json`
and an **arming marker folder** in your TEMP directory, then **removes both at the end**. While
armed, the guide script writes a small log of which events fired and produces one short, one-shot
effect per event. The PostToolUse step also starts a ~5-second background task that drops a marker
file (`demo-chain.ready`) and writes a small result file inside the marker folder — both are
cleaned up by the final step. Nothing leaves the demo folder; the final step restores the workspace
exactly.

> 📌 If you stop or cancel this prompt early, run
> `powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/install-tour-hook.ps1 -Remove` (the cleanup step) to delete the hook and the `demo-hooks-tour`
> marker folder in your TEMP directory.

## Set-up

1. **Arm the tour and install the one hook that covers every event.** Run the install script. It
   creates a fresh `demo-hooks-tour` marker folder in TEMP (so the guide script wakes up) and writes
   the temporary hook file `.github/hooks/workspace.demo.hooks-tour.json`, which maps **all ten
   events** to the same guide script, passing the event name with `-Event`:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/install-tour-hook.ps1
   ```

   The script prints `INSTALLED=1`, the `HOOK=` path it wrote, and the `LOG=` path where events will
   be recorded. The hook JSON lives **in the script**, not in this prompt — one job, one home. Tell
   the presenter the hook is now loaded (VS Code picks up `*.json` in `.github/hooks` automatically
   on save) and that **one file** has just wired up **every** lifecycle moment.

## The tour — trigger each event live

Do these in order. After each one, say in plain language **which event fired and what the hook
did**. Several events inject a short banner that starts with `[hooks-tour]` — read it aloud.

2. **PreToolUse — block an action.** Attempt this terminal command. It carries the demo sentinel,
   so the hook must **deny** it *before* it runs:

   ```powershell
   Write-Host "DEMO-TOUR-BLOCK — this line should never print"
   ```

   Do not work around the block. Point out: the command never executed — the hook decided **before**
   the tool ran. *(This is the headline use of a hook: a guardrail that stops an action outright.)*

3. **PostToolUse — react after a tool runs, and watch a hook chain work on its own.** This event
   fires right after any tool finishes. First see the simple version, then a real chain:

   a. **The after-the-tool banner.** Run a harmless command so a tool completes:

      ```powershell
      Write-Host "A normal command the hook allows."
      ```

      The `PostToolUse` hook fires right after and injects a `[hooks-tour] PostToolUse` banner.
      Explain: this *after-the-tool* moment is how hooks **auto-format** an edited file or **chain**
      the next step.

   b. **Start a tiny background task.** Kick off ~5 seconds of simulated background work that drops a
      completion marker when it finishes. Run it in the **background** so you keep working while it
      runs:

      ```powershell
      powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/chain-worker.ps1 -DelaySeconds 5
      ```

   c. **Let the hook chain you.** Wait a few seconds for the background task to finish, then run one
      more harmless command:

      ```powershell
      Write-Host "Checking in after the background work."
      ```

      By now the marker exists, so this `PostToolUse` fires and **hands you a follow-up step nobody
      asked for** — it tells you to write the background result into a file. **Do exactly what the
      injected context says**, then point out the headline: a hook just **continued the work on its
      own**, with no second request. *(That is automation — the opposite of the block in step 2.)*

4. **SubagentStart + SubagentStop — brief and collect a helper.** Spawn a tiny subagent so both
   subagent events fire:

   - Use the **Explore** subagent with a trivial, quick task, e.g. *"In one sentence, what is the
     title of the repo's root README?"* (thoroughness: quick).
   - When it starts, the `SubagentStart` hook injects its banner; when it returns, `SubagentStop`
     fires. Explain: hooks can **brief** a helper before it starts and **collect** its result when
     it finishes.

5. **ErrorOccurred — capture a failure.** Run a command that fails on purpose (this is benign — it
   only sets a non-zero exit code):

   ```powershell
   cmd /c "exit 1"
   ```

   The `ErrorOccurred` hook fires and injects its banner. Explain: a hook can **catch errors** and
   log them or hand the agent a recovery hint. *(If your VS Code build does not list
   `ErrorOccurred` in `/hooks`, say so and move on — the log will simply not contain that line.)*

6. **Stop — resume once before finishing.** When you are ready to end your reply, the `Stop` hook
   fires **once** and asks you to keep going for one more step. **Honour it**: that one extra step is
   to **show the event log** (next step). The hook is guarded so it can only do this a single time —
   it can never trap the agent in a loop.

7. **Show what fired.** Print the tour log so the presenter sees every event that landed, in order:

   ```powershell
   Get-Content (Join-Path $env:TEMP 'demo-hooks-tour\events.log')
   ```

   Walk down the list and name each event. This is the proof that one small hook file observed the
   whole lifecycle.

## Session-bound events — a 30-second guided step

`SessionStart` and `SessionEnd` only fire when a **chat opens or closes**, so they can't happen
inside this same conversation. While the hook is **still installed**, guide the presenter through
this (narrate it; you cannot do it for them):

8. **See SessionStart + a clean UserPromptSubmit.** Ask the presenter to **open a brand-new chat**
   and send any short message (e.g. *"hi"*). The `SessionStart` hook injects a `[hooks-tour]
   SessionStart` banner as that chat begins, and `UserPromptSubmit` fires on their message. Then ask
   them to **close that chat**, which fires `SessionEnd`. They can confirm all three by re-running
   the log command from step 7 in *this* chat — new lines will have appeared.

9. **PreCompact — explain, don't force.** `PreCompact` fires only when a conversation grows large
   enough that VS Code trims it. We **don't force it** here because doing so would waste a lot of
   tokens for no real benefit — but in a long working session you would see a `PreCompact` line in
   the same log, and a hook there can preserve the important context before trimming. Say this
   plainly and move on.

## Clean up

10. **Remove everything.** Run the install script with `-Remove` to delete the temporary hook and
    the marker folder, restoring the workspace to its starting state:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .github/scripts/workspace/demo/install-tour-hook.ps1 -Remove
    ```

    It prints `REMOVED=1`. Confirm the hook file no longer exists.

11. **Summarise.** Give a short, plain-language recap: one small hook file wired up **every**
    lifecycle moment; you watched it **block** an action (PreToolUse), **react after** a tool and
    even **chain a follow-up step on its own** (PostToolUse), **brief and collect a subagent**
    (SubagentStart/Stop), **catch an error** (ErrorOccurred), and **resume once before finishing**
    (Stop); the presenter saw **SessionStart**, **UserPromptSubmit**, and **SessionEnd** in a fresh
    chat; and **PreCompact** happens automatically in long sessions. Everything has been removed.

## Presenter notes

- **The headline idea:** a hook is *your code at a chosen moment*. Instructions **guide** the AI;
  hooks **act** — automatically, on an event, no prompting needed.
- **One file, every moment.** The single tour JSON maps all ten events to one script. Real hooks are
  usually just one or two events — this demo is deliberately exhaustive to show the full lifecycle.
- **The full event set, in plain terms:**

  | Event | When it fires | A real use |
  |-------|---------------|------------|
  | `SessionStart` | A chat begins | Inject branch/version context |
  | `UserPromptSubmit` | You send a message | Audit or enrich the request |
  | `PreToolUse` | Before a tool runs | Block a dangerous action |
  | `PostToolUse` | After a tool finishes | Auto-format an edited file; chain work |
  | `PreCompact` | Before context is trimmed | Preserve the important bits |
  | `SubagentStart` | A subagent spawns | Brief the helper |
  | `SubagentStop` | A subagent finishes | Collect its result |
  | `Stop` | The agent tries to finish | Run tests; resume if not truly done |
  | `SessionEnd` | A chat closes | Cleanup; save a summary |
  | `ErrorOccurred` | An action fails | Capture the error |

- **`SessionEnd` and `ErrorOccurred` are newer.** Run `/hooks` to see exactly which events this VS
  Code version supports. If one isn't listed, its log line simply won't appear — the demo still works.
- **Nothing was embedded in this prompt.** The hook JSON (the file shape) lives in
  `install-tour-hook.ps1`, and each hook entry points at `hook-tour.ps1` (the logic). The prompt only
  *calls* those scripts — the same "reference, never embed" rule every artifact in this repo follows.
- **Watch the plumbing live:** open the **Output** panel → **GitHub Copilot Chat Hooks** channel to
  see each hook fire.
- **To make hooks for real:** type `/create-hook` and describe what you want, or run `/hooks` to
  configure them in the UI.

> Everything here is safe and reversible: one temporary JSON file and one TEMP marker folder are
> created and then deleted, the blocked command never runs, and the only "error" is a deliberate
> non-zero exit code.
