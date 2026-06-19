---
agent: agent
description: 'Run a non-breaking timed loop that holds the agent, so you can demo Steering, queued messages, and Stop while a prompt is running.'
---

# Steering and Queueing

Run a **single, non-breaking, foreground loop** that keeps you busy for exactly
`${input:minutes:How many minutes should the loop run?}` minutes. Its only purpose
is to produce a steady stream of terminal output **while a prompt is running**, so
the presenter can demonstrate the chat controls that are only available during an
active run:

- **Steering** — sending a message while the agent is working to steer it.
- **Queued messages** — messages you type during the run that are held and picked
  up after the current step.
- **Stop** — cancelling the in-progress run from the chat input.

## What to do

1. Run the loop below **once**, in the terminal, in **synchronous (foreground)
   mode**, so you wait for it to finish. Do **not** run it in the background.
   The `${input:minutes}` placeholder is filled in automatically when the prompt
   runs — do not edit `$minutes` by hand.
2. While it runs, do nothing else — just let the output stream.
3. When it finishes, reply with a one-line confirmation: how long it ran and how
   many ticks it printed.

Run the loop via [`.github/scripts/workspace/demo/steering-loop.ps1`](../../../scripts/workspace/demo/steering-loop.ps1) — it owns the countdown logic so nothing runnable is embedded in this prompt. The `${input:minutes}` placeholder is filled in automatically when the prompt runs:

```powershell
powershell.exe -ExecutionPolicy Bypass -File ".github/scripts/workspace/demo/steering-loop.ps1" -Minutes ${input:minutes}
```

## Presenter notes

- **Steering:** while the loop streams, type a message and send it to steer the
  agent mid-run.
- **Queued messages:** type follow-up messages during the run; they queue and are
  picked up after the current step completes.
- **Stop:** press Stop to cancel the run at any moment.

> This loop is intentionally idle work (a countdown). It changes nothing on disk
> and is safe to cancel at any moment.
