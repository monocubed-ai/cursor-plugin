---
name: book-a-job
description: Book work into FieldCamp — create a job for a client with priced line items, schedule a visit, and assign a technician. Use for "book a service call", "create a job for X", "schedule a visit", "add a job with these parts".
---

# Book a job

Creating a job writes to the customer's live operation. Resolve the real client and the
real service first, confirm the details back to the user, then create.

## 1. Resolve the client

Never invent a `clientId`. Look it up:

```
get_filtered_clients({ filters: [], limit: 10 })          // filters is required
```

Search by name if you have one, then take the client's id from the result. If several
match, ask which — booking against the wrong client is worse than one extra question.

If the client genuinely does not exist yet, `create_client` needs at least `firstName`
**or** `email`.

## 2. Resolve the service and its price

```
get_products_services({ filters: [], limit: 20 })
```

Use the stored `price` rather than a price the user guessed, unless they explicitly
override it. `get_taxes` gives tax ids if the job needs one.

## 3. Create the job

All fields go **inside** `job_data` — top-level keys are rejected.

```
create_job({ job_data: {
  clientId: "<24-hex ObjectId>",
  jobType: "one-off",                       // or "recurring"
  startDateTime: "2026-09-10T04:30:00.000Z",
  endDateTime:   "2026-09-10T05:30:00.000Z",
  jobItems: [
    { itemName: "AC Service Call", price: 150, quantity: 1 }
  ]
}})
```

### Line items

- `itemName` and `price` are **both required**. Omitting either fails.
- The catalogue key is `itemId` — **not** `productServiceId` and not `id`.
- `total` per line is derived as `price × quantity` if you omit it.
- The job's `subTotal` and `total` are derived from the line items, so a job created with
  priced items no longer stores 0. If you pass `subTotal`/`total` yourself, yours win.

### Unknown fields are rejected, not ignored

The server validates the payload against an allow-list. A misspelled or invented key
returns a 400 that **names the valid fields** — read that list and correct the call
rather than retrying the same shape.

### Linking to a custom-object record

`linkedRecords` is **not accepted**. To link a job to a Unit, Asset or similar, use:

```
targetRecordId: "<record id>", targetObjectSlug: "<slug>"
```

Get the slug from `list_object_definitions` and use it verbatim.

## 4. Schedule and assign

- `create_visit` — add a visit to the job
- `update_job` — change fields later (this **overwrites** what you set, so send only what changes)
- Check availability first with `get_available_team_members_schedule` (see the
  `daily-dispatch` skill) rather than assigning blind

## Recurring jobs

If `jobType` is `"recurring"`, supply `repeatOptions`. A recurring job created without it
is accepted and produces **zero visits** — it looks successful and dispatches nothing.

## Confirm before writing

Read back client, date, time, service and price, and get a yes. `create_job` is additive
so a mistake is recoverable, but a wrong job on a real schedule sends someone to the
wrong address.
