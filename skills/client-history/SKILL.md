---
name: client-history
description: Everything about one customer — their details, past and upcoming jobs, documents, what they have paid, and the audit trail of who changed a record and when. Use for "what's the history with this client", "what did we do for them last time", "who changed this job", "pull up their invoices".
---

# Client and record history

## Find the client

```
get_filtered_clients({ filters: [], limit: 10 })      // filters is required
get_client_by_id({ client_id: "<24-hex ObjectId>" })
```

Then the surrounding detail:

- `get_client_documents` — their estimates and invoices
- `get_client_payment_history` — what they have paid
- `get_client_products` — products or services attached to them
- `get_tasks_by_client` — open tasks
- `get_filtered_jobs` with a `clientId` filter — their job history

## Audit trail: who changed what

`get_history` takes a required `module_id` (a 24-character hex ObjectId) and a
`module_type`:

```
get_history({ module_type: "job", module_id: "<job id>" })
```

`module_type` accepts:

- `"job"`
- `"visit"`
- **a custom-object slug** — pass the `slug` from `list_object_definitions` **verbatim**.
  It is not the plural form and not the display name; real slugs look like `warnty`,
  `contract_renewal`, `all_mode`.

Each entry gives `action`, a human-readable `description`, `metadata` with old and new
values, and `createdByUser`.

### An empty history is not "nothing changed"

- For a valid type it means nothing has been recorded for **that record** yet.
- `"client"` and `"request"` return empty by design — client activity lives in a separate
  store this endpoint does not read, and request activity is not recorded at all.

Either way, do not tell the user "nothing has changed". Say history is not recorded for
that type, or that this record has no entries yet.

### A wrong slug looks identical to no history

Passing a plural or a display name returns a clean empty result, not an error. If you
expected entries and got none, re-check the slug against `list_object_definitions` before
concluding anything.

## Custom objects (Units, Assets, Contracts…)

Orgs model their own record types. To explore them:

- `list_object_definitions` — the slugs, with record counts
- `list_records({ slug: "warnty", limit: 10 })` — **the parameter is `slug`**, not
  `object_slug`; the wrong name is refused by the permission layer
- `get_record`, `get_record_summary` — one record
- `resolve_record_hierarchy` — a record's parent/child chain (read-only despite the name)

## Ordering and gaps

History is chronological. If a job has a `created` entry but the user is asking about an
edit that is not there, say so rather than inferring — a missing entry means the change
was not recorded, not that it did not happen.
