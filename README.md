# FieldCamp for Cursor

Run your field service operation from the agent. Ask what is on the board today, find out
who is genuinely free for a slot, book a job with priced line items, chase unpaid
invoices, pull a customer's history, or check whether a part is in the van — against your
live [FieldCamp](https://fieldcamp.ai) data.

This plugin connects Cursor to the FieldCamp MCP server (~98 tools) and adds five skills
that wrap the workflows operators actually run.

## Setup

### 1. Create an API token

In FieldCamp: **Settings → API Keys → Create key**. The token starts with `fc_live_`.

The token carries **your own FieldCamp permissions**. The agent can only see and change
what your user account can — a dispatcher's token cannot do what an admin's can.

### 2. Install the plugin

Cursor: **Settings → Plugins → find "fieldcamp" → Install**.

### 3. Paste the token

Cursor will ask for `FIELDCAMP_API_TOKEN`. Paste the `fc_live_…` value.

The token is stored by Cursor, not in this repository — this repo contains no secrets and
never will.

### 4. Check it works

Ask the agent:

> Show me my scheduled jobs and who they're assigned to

You should get a list of real jobs with clients, status and totals.

## What the skills cover

| Skill | Use it for |
|---|---|
| **daily-dispatch** | What is scheduled, which jobs have nobody assigned, who is free for a slot, whether a proposed time clashes |
| **book-a-job** | Create a job for a client with priced line items, schedule a visit, assign a technician |
| **unpaid-invoices** | Find outstanding invoices, see what a client owes, record a payment that already arrived, email a document |
| **client-history** | One customer's jobs, documents and payments, plus the audit trail of who changed a record and when |
| **parts-and-inventory** | Stock on hand and where, moving stock between locations, prices, suppliers, purchase orders |

The skills carry the shapes the API actually expects — required `filters` arrays, the
numeric `documentType`, the `locationId` key for stock, the `targetRecordId` pair for
linking custom objects. That is the difference between a request that works first time and
one that comes back with a validation error.

## What the agent will and will not do

Read tools (today's jobs, availability, client history, stock) run freely.

Writes are annotated so Cursor can prompt you first:

- **Additive** — `create_job`, `create_client`, `create_visit`, `create_document`. These
  add a record and change nothing existing.
- **Destructive** — every `update_*` and `delete_*`, plus `record_payment`,
  `transfer_inventory` and the stage/action tools. These overwrite or remove data.
- **Leaves FieldCamp** — `send_document_email` reaches a real inbox and cannot be unsent.
  `create_task` can send an email or SMS reminder to the assignee. The calendar tools
  propagate to any connected external calendar.

Nothing in this plugin moves money. `record_payment` writes a bookkeeping entry for a
payment that already happened; it never charges a card or contacts a payment provider.

## Alternative: OAuth instead of a token

The FieldCamp MCP server also supports OAuth 2.1 with dynamic client registration, so you
can connect it as a remote MCP server in Cursor and sign in through the browser instead of
pasting a token. The plugin ships the token path because it is one field and works
immediately; see the [MCP docs](https://docs.fieldcamp.ai/integrations/mcp-server) if you
would rather use OAuth.

## Developing locally

```bash
git clone https://github.com/fieldcampai/cursor-plugin
mkdir -p ~/.cursor/plugins/local
ln -s "$PWD/cursor-plugin" ~/.cursor/plugins/local/fieldcamp
```

Restart Cursor, set `FIELDCAMP_API_TOKEN`, and the plugin loads from your working copy.

To check the endpoint directly:

```bash
curl -s -X POST https://mcp.fieldcamp.ai/mcp \
  -H "Authorization: Bearer $FIELDCAMP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'
```

A `200` with a `serverInfo` block means the endpoint and your token are both good.

## Layout

```
.cursor-plugin/plugin.json   manifest — declares skills, MCP config and the token variable
mcp.json                     remote MCP server, streamable-http, token in a header
skills/*/SKILL.md            five workflow skills
assets/logo.svg              plugin logo
```

## Links

- FieldCamp — https://fieldcamp.ai
- MCP integration docs — https://docs.fieldcamp.ai/integrations/mcp-server
- Support — support@fieldcamp.ai

## License

MIT — see [LICENSE](LICENSE).
