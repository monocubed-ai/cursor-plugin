---
name: unpaid-invoices
description: Chase money — find unpaid or overdue invoices, see what a client owes, record a payment that has already arrived, and email a document to the customer. Use for "who owes us money", "unpaid invoices", "mark this invoice paid", "send the invoice to the client".
---

# Unpaid invoices and payments

## Find the invoices

`get_invoices` needs two things, and both trip people up:

```
get_invoices({ filters: [], limit: 20, documentType: 1 })
```

- `filters` is **required** even when empty — pass `[]`.
- `documentType` is **required** and must be a **number**, not a string:
  - `1` = Invoices
  - `2` = Estimates

`documentType: "1"` (quoted) is rejected, and so is omitting it — both return
`documentType must be 1 (Invoices) or 2 (Estimates)`. The word `"invoice"` is rejected too.

Results come back under `data.documents`, each with `documentNumber`, `documentType`,
`title`, `total` and `paymentStatus`. Read `paymentStatus` to sort paid from outstanding.

Related reads:

- `get_invoice_by_id` — one document in full
- `get_client_payment_history` — everything one client has paid
- `get_payment_history` — payments across the org
- `get_document_number` — the next document number

## Record a payment

`record_payment` writes a payment that has **already happened elsewhere** — cash, a bank
transfer, a card charge taken in the field. It is a bookkeeping entry.

```
record_payment({
  documentId: "<invoice id>",
  amount: 150,
  date: "2026-09-09",
  method: "cash",
  note: "collected on site"
})
```

**It does not move money.** It never charges a card and never contacts a payment
provider. If the user wants to actually take a payment, that happens in FieldCamp or
through their payment provider — say so plainly rather than implying the agent can charge
a customer.

It updates the document's paid balance, so it is a destructive write: confirm the amount
and the invoice with the user first, and never guess an amount.

`delete_payment` reverses a mistaken entry.

## Email a document to the customer

`send_document_email` delivers an invoice or estimate to a real inbox.

```
send_document_email({
  documentId: "<id>",
  to: ["customer@example.com"],
  subject: "Invoice 1042 from Acme Heating",
  message: "..."
})
```

This leaves FieldCamp and **cannot be unsent**. Always show the user the recipient list
and the subject and get an explicit yes before calling it. Do not send to an address the
user has not given you or that is not already on the record.

## Reporting

For "how much are we owed", prefer `get_analytics` with a `metric` (it is required — e.g.
`outstandingRevenue`, `totalClients`) over adding up invoice rows yourself. If the metric
comes back empty, say it is unavailable rather than silently computing a different number.

## Be careful with money

- Never state a total you have not read from a tool result.
- If an invoice's `total` looks wrong, report what the record says rather than correcting
  it silently — the user needs to know the data is off.
- Amounts are in the organisation's own currency; do not convert or add a symbol you have
  not seen in the data.
