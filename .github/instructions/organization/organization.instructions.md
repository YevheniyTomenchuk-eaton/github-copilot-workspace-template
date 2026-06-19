---
applyTo: "organization/**"
---

# Organization — AI Instructions

## What Is the Organization?

The `organization/` folder is the **central source of truth** for all people,
locations (parties), roles, teams, ceremonies, and team planning on the project.
It is published on GitHub Pages for human consumption.

Other sections (toolkit, agenda, etc.) **link to** the organization — they never
duplicate people, roles, or team data.

> This folder ships as a **placeholder example** in the template. Replace the
> sample sites, people, roles, and teams with your own.

## Core Structural Principle

**Every named concept gets its own folder with a `README.md`.** This applies
universally:

- Each **person** → `people/{name}/README.md`
- Each **party** → `foundation/parties/{name}/README.md`
- Each **role** → `foundation/roles/{name}/README.md`
- Each **team** → `foundation/teams/{name}/README.md`
- Each **ceremony** → `ceremonies/{name}/README.md`

**Never** create a bare `.md` file where a folder with `README.md` belongs. The
folder name defines the concept; the `README.md` describes it.

## Folder Structure

```
organization/
├── README.md                               ← dashboard
├── foundation/
│   ├── parties/
│   │   ├── site-a/README.md
│   │   └── site-b/README.md
│   ├── roles/
│   │   ├── developer/README.md
│   │   ├── qa/README.md
│   │   └── manager/README.md
│   └── teams/
│       ├── team-alpha/README.md
│       └── team-beta/README.md
├── people/
│   └── {firstname-lastname}/README.md
├── ceremonies/
│   ├── daily-standup/README.md
│   ├── sprint-planning/README.md
│   └── sprint-review/README.md
└── team-plan/
    └── README.md
```

## Content Rules

### Human-Only Pages

All files in `organization/` are published on GitHub Pages for **human readers**.
Never include AI-specific guidance (prompt patterns, instruction references) in
these pages.

### Availability

- If a person has limited availability, show it: `Until Apr 2026`.
- If a person has no limit, **omit the Availability field entirely** — do not
  write "permanent", "unlimited", or "infinite".

### Linking Rules

- **Always link to `README.md`** — never link to a bare folder path.
- **Roles** → `organization/foundation/roles/{role}/README.md`
- **Parties** → `organization/foundation/parties/{party}/README.md`
- **Teams** → `organization/foundation/teams/{team}/README.md`
- **People** → `organization/people/{person}/README.md`
- **Ceremonies** → `organization/ceremonies/{ceremony}/README.md`
- Use relative paths from the linking file.

### Person Pages

Each person has a folder: `organization/people/{firstname-lastname}/README.md`

Use the [person template](../../templates/organization/people/organization.people.template.md).

Required fields in the info table:

| Field | Required | Notes |
|-------|----------|-------|
| **Email** | Always | Email address |
| **Party** | Always | Linked to `foundation/parties/{party}/README.md` |
| **Role** | Always | Linked to `foundation/roles/{role}/README.md`. Comma-separated if multiple. |
| **Team** | If in a scrum team | Linked to `foundation/teams/{team}/README.md`. Comma-separated if multiple. |
| **Allocation** | Always | Percentage (100%, 50%) or "On demand" |
| **Availability** | Only if limited | e.g., "Until Apr 2026". Omit if not limited. |

### Adding a New Person

1. Create folder: `organization/people/{firstname-lastname}/`
2. Copy [person template](../../templates/organization/people/organization.people.template.md) → `README.md`
3. Fill in all fields
4. Add the person to the appropriate party table in `organization/people/README.md`
5. Add the person to `organization/README.md` Quick Contacts table
6. If in a scrum team, add to `organization/team-plan/README.md`

### Adding a New Foundation Item

Each gets its own folder:

- **Party:** Create `organization/foundation/parties/{name}/README.md`, add to `parties/README.md` table
- **Role:** Create `organization/foundation/roles/{name}/README.md`, add to `roles/README.md` table
- **Team:** Create `organization/foundation/teams/{name}/README.md`, add to `teams/README.md` table

### Adding a New Ceremony

Create folder `organization/ceremonies/{name}/` with `README.md` inside. Include a
details table (Cadence, Duration, Scope) and a Participants section. Add to
`ceremonies/README.md` overview table.

## Naming Conventions

- **Person folders:** `{firstname}-{lastname}` — e.g., `alex-carter/`
- **Foundation folders:** lowercase kebab-case — e.g., `developer/`, `site-a/`, `team-alpha/`
- **Ceremony folders:** lowercase kebab-case — e.g., `daily-standup/`, `sprint-planning/`

## Front Matter

Person pages use:

```yaml
---
title: "{Full Name}"
parent: "People"
grand_parent: "Organization"
---
```

Foundation items use `grand_parent: "Organization Classification"` when their
parent title could be non-unique.

## How Other Sections Use the Organization

### Toolkit — Email

The [Email toolkit](../../../toolkit/email/README.md) can resolve a recipient's
display name and address from a person page instead of hardcoding them. The actual
people data lives in the published organization pages.

### Toolkit — Agenda / Meetings

Agenda or meeting pages link presenters and attendees to
`organization/people/{person}/README.md` and roles to
`organization/foundation/roles/{role}/README.md`.
