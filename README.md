# Suvidha FinServe

A fictional Indian accounting/bookkeeping firm ("Suvidha" =
"convenience/facility" in Hindi) offering GST filing, invoicing, and
payroll services to small/medium Indian businesses, used as a
**reference project for integrating the [`weave`](../weave) SDK**. This
repo is entirely independent of `weave/` — its own git history, its own
dependencies — exactly the shape a real Weave tenant's integration
takes: a business's own code, in a business's own codebase, never
inside the platform repo itself.

This project's sibling, [`../tarang-electronics`](../tarang-electronics),
walks the same integration for a retail-to-consumer (B2C) business.
Suvidha is deliberately different: its "customers" are other businesses
— its own bookkeeping/GST/payroll clients checking their own account —
not individual end consumers. Together the pair shows the SDK isn't
tied to one domain shape.

Read this file (and `onboard.py`, `api.py`) to learn exactly how to
wire an existing business's systems into Weave. Nothing here is a toy
stand-in for "real code" — `api.py` is a genuine FastAPI service with
the kind of client-facing/internal-staff route split any professional
services firm would already have, and `onboard.py` calls the exact same
SDK/RPC surface a real integrator would.

## The six-step onboarding flow

Every business connecting to Weave goes through the same sequence.
`onboard.py` narrates each step explicitly as it runs; here's what each
one means and where the code for it lives.

1. **Sign up** — `CreateTenant` + `Register` an owner account, via a
   single `weave.sign_up()` call. These are `core`'s real public
   bootstrap RPCs, unauthenticated by design (there's no token to present
   before a tenant/user exists at all). See `onboard.py`'s `_step1_sign_up`.
2. **Authenticate** — `Login` to get a JWT, exactly as any caller (the SDK,
   `weave/web`, or a hand-rolled integration) would.
3. **Describe the business's systems** — `weave.connect()` then repeated
   `add_tool()` calls, one per existing HTTP endpoint Suvidha wants
   Weave to reason over. Each call makes a deliberate `visibility`
   (`external`/`internal`) and `category` (`general`/`analytics`)
   decision — see the comments in `onboard.py` for why each of the 8
   tools here got the value it did. (A business with a much larger API —
   dozens to hundreds of routes — doesn't have to hand-write one
   `add_tool()` call per endpoint: `client.add_tools_from_openapi()`
   registers a deliberate subset of an existing OpenAPI spec in one call.
   Suvidha's own API is small enough that hand-written calls are clearer
   to read as a tutorial, so `onboard.py` doesn't use it, but see
   `weave/docs/architecture/ARCHITECTURE.md` §3 for how it works.) A tool
   can also be marked `auth_mode="user_token"` for an endpoint that must
   answer only for the specific signed-in client asking — genuinely
   relevant to Suvidha's actual shape (`check_gst_filing_status`,
   `get_invoice_status` — a real accounting firm would want each client
   restricted to their *own* filings/invoices, never another client's,
   the same restriction this project's guardrails already describe in
   prose for the external profile). `onboard.py` still registers every
   tool at the default `auth_mode="none"` to keep the six-step walkthrough
   focused on the onboarding *sequence* rather than this one additional
   decision — see `ARCHITECTURE.md` §3 for the full per-user-auth
   mechanism a real deployment would layer on top.
4. **Shape the bots** — `create_bot_profile()` once per distinct audience.
   Suvidha has two: `external` (its own clients, on the `web-widget`
   channel, guarded so one client can never see another client's data,
   P&L detail, or ledger entries) and `internal` (Suvidha's own staff,
   on `slack`, sees everything). Each profile can also set its own
   `persona` (the literal system-prompt text for that bot — see `weave`'s
   `create_bot_profile()` docstring) and choose which LLM backend
   generates its answers via `llm_provider`/`llm_model` (defaults to
   orchestrator's local Ollama model if left unset); this project's
   `onboard.py` doesn't set either, relying on those defaults, but a real
   integrator often would.
5. **Connect a channel** — the step this reference project intentionally
   stops short of automating, since it's specific to how *you* reach your
   users: embed `weave/web`'s chat widget on your own site pointed at the
   external profile's `web-widget` channel, and/or wire a Slack app
   pointed at the internal profile's `slack` channel. Nothing today
   listens on either channel for this fictional tenant — `onboard.py`
   prints this explicitly rather than silently skipping it.
6. **Go live** — once a channel exists, real end users interact through
   it. Until then, verify the exact same `ChatStream` RPC a real channel
   would call using `weave`'s own dev harness (see **Verifying** below).

## Layout

- `data.py` — canned in-memory data: client companies, invoices, GST
  filings, payroll runs, and internal-only P&L financials/ledger
  entries per client.
- `api.py` — the FastAPI service. 3 external routes (GST filing status,
  invoice status, payroll run status), 5 internal-only routes (client
  contact PII, P&L financials, raw ledger entries, revenue analytics,
  client-retention analytics).
- `onboard.py` — runs the six-step flow above against a real running
  Weave `core`.
- `tests/test_api.py` — asserts the external/internal field split holds
  (e.g. the external invoice/GST/payroll routes never leak amounts or
  totals meant only for internal use) alongside ordinary endpoint
  correctness.

## Running it

Requires a sibling `weave/` checkout (this project depends on
`weave/packages/weave-sdk` as a path dependency — see `initialize.sh` —
the same way a real integrator would pre-release; swap for `pip install
weave-sdk` once it's published, with zero other code changes) and
weave's own stack already running (`core` + Mongo/Redis/Qdrant, plus
`mcp-gateway` — see `weave/PLAN.md` and `weave/infra/`). The `weave` SDK
is self-contained (bundles its own generated gRPC stubs — see
`weave/packages/weave-sdk/weave/_core_client.py`), so this is the only
package this project needs from `weave/` — no separate
`weave/packages/shared-clients` install step.

```bash
./initialize.sh              # venv, deps, proto codegen, starts api.py on :9102
```

In a second shell, once the API is up:

```bash
./.venv/Scripts/python.exe onboard.py
```

This prints `tenant_id`/`owner_email`/`owner_password` at the end —
save them for verification.

### Tests

```bash
./.venv/Scripts/python.exe -m pytest
```

### Verifying (step 6)

Using `weave/orchestrator`'s own dev harness against the tenant
`onboard.py` just created. The owner account `onboard.py` registers has
role `owner`, which the `external` profile's `roles_allowed` (customer
only) correctly rejects — verify against the `internal` profile's
`slack` channel instead:

```bash
cd ../weave/orchestrator
./.venv/Scripts/python.exe dev_cli.py \
  --tenant-id <tenant_id> --email owner@suvidha-finserve.test --password hunter2hunter2 \
  --channel slack "What's the status of invoice INV-2003?"
```

This exercises the exact `ChatStream` RPC a real channel integration
would call — dynamic tool discovery and (for a real `customer`-role
caller against the `external` profile's `web-widget` channel) the
external visibility filter and guardrails all apply exactly as they
would for a real client.

## Config

| Env var | Default | Meaning |
|---|---|---|
| `DEMO_PORT` | `9102` | Port `api.py` listens on |
| `WEAVE_REPO` | `../weave` | Path to the sibling `weave/` checkout |
| `CORE_ADDR` | `localhost:9090` | `core`'s gRPC address |
| `DEMO_API_URL` | `http://localhost:9102` | Where `onboard.py` registers tools against |
| `DEMO_OWNER_EMAIL` / `DEMO_OWNER_PASSWORD` | `owner@suvidha-finserve.test` / `hunter2hunter2` | Owner account created in step 1 |
