---
name: workspace-demo-clarifying-questions
description: 'Force the agent to ask clarifying questions before acting, to showcase the interactive question control.'
---

# Clarifying Questions

This skill is intentionally **ambiguous and underspecified**. Before doing any
work, you **must stop and ask the presenter clarifying questions** using the
interactive question control. Do **not** guess, and do **not** start any
implementation until the presenter has answered.

## The (deliberately vague) request

> "Set up the thing we talked about for the demo so it looks right on screen."

## What to do

1. Do **not** take any action yet.
2. Ask the presenter a small set of clarifying questions using the interactive
   ask-questions control. Present them as selectable options where possible, with
   one recommended default each. Cover at least these unknowns:
   - **What is "the thing"?** (e.g., a sample file, a diagram, a config block, a
     terminal output) — provide a few options.
   - **Where should it go?** (which folder / file) — provide a few options.
   - **What does "looks right on screen" mean?** (e.g., specific formatting,
     color theme, font size, a particular layout) — provide a few options.
   - **How long should it stay?** (temporary / keep it) — provide options.
3. Wait for the answers.
4. Only after receiving answers, briefly restate what you now understand — but
   you do **not** need to actually build anything. This skill is for
   demonstrating the question-and-answer interaction, not for producing output.

## Presenter notes

- This showcases the agent pausing to collect input through selectable option
  prompts (with optional free-text answers) before proceeding.
- Answer the questions live to show the round-trip, then end the demo.
