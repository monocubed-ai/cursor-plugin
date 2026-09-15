---
name: daily-dispatch
description: Review the work board and fill gaps — what is scheduled, which jobs have nobody assigned, who is genuinely free for a slot, and whether a proposed time clashes. Use for "what's on today", "who can take this", "is anyone free Thursday afternoon", "which jobs are unassigned".
---

# Daily dispatch

Answer scheduling questions from live FieldCamp data. Never guess a technician's
availability — the server knows working hours, days off and existing visits.

## Read the board

`get_filtered_jobs` — **`filters` is required even when you have no filter.** Pass
`filters: []` or the call fails with `filters parameter is required and must be an array`.

```
get_filtered_jobs({ filters: [], limit: 20 })
```

To narrow by date, use two clauses on `startDateTime`:

```
get_filtered_jobs({ limit: 20, filters: [
  { field: "startDateTime", condition: "after",  filterCondition: "",    value: "2026-09-09" },
  { field: "startDateTime", condition: "before", filterCondition: "and", value: "2026-09-10" }
]})
```

Keep `limit` low. A 30-job response is already ~50 KB; asking for a whole month will
crowd out the rest of the conversation.

Each job returns `jobNumber`, `startDateTime`, `jobStatus`, `client`, `jobAddress`,
`total` and `assignedToTeams`. **An empty `assignedToTeams` means nobody is assigned** —
call that out, it is the most common real gap on a work board.

## Find who is free

`get_available_team_members_schedule` needs all three of these, and the parameter names
are `visit`-prefixed:

```
get_available_team_members_schedule({
  visitStartDateTime: "2026-09-09T03:30:00.000Z",   // UTC
  visitEndDateTime:   "2026-09-09T05:30:00.000Z",
  timezone: "Asia/Kolkata"                          // IANA name, required
})
```

The response is the useful part: `availableTeamMembers` (with `role` and `skills`),
`totalCount`, `busyCount`, and `unavailableReasons` — a per-person reason such as
"Has another visit at this time", "Outside working hours" or "Not available on Thursdays".

**Always report the reasons, not just the count.** "12 people are busy because they
already have a visit" is a scheduling answer; "12 unavailable" is not.

Prefer technicians (`role` containing `fieldTechnician`) when the user is dispatching
field work, and mention their `skills` so the user can match the job.

## Check a specific clash

`check_team_schedule_conflicts` evaluates a proposed window against named people. It is
read-only — it books nothing — so use it freely before suggesting a time.

## Also useful

- `get_visits_for_job` — the visits under one job
- `get_company_schedule` — the org's business hours
- `get_teams` / `get_all_team_members` — the roster with skills and assignability
- `get_dispatch_suggestions` — the server's own suggestions for a job

## Watch out

- `get_visit_stats` and `get_calendar_events` can return over a megabyte. Only call them
  with narrow filters, and never to "have a look".
- Not everyone on the roster is a field technician. Many orgs mark dispatchers and admins
  `isAssignableToJobs: true`, which makes the dispatch pool look larger than it is.
- A member with a `pending` or `expired` `invitationStatus` can be assigned but has not
  accepted, so the job will not appear in their app. Flag it rather than assigning silently.
