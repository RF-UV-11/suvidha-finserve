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

1. **Sign up** — `CreateTenant` + `Register` an owner account. These are
   `core`'s real public bootstrap RPCs, unauthenticated by design (there's
   no token to present before a tenant/user exists at all). See
   `onboard.py`'s `_step1_sign_up_and_step2_authenticate`.
2. **Authenticate** — `Login` to get a JWT, exactly as any caller (the SDK,
   `weave/web`, or a hand-rolled integration) would.
3. **Describe the business's systems** — `weave.connect()` then repeated
   `add_tool()` calls, one per existing HTTP endpoint Suvidha wants
   Weave to reason over. Each call makes a deliberate `visibility`
   (`external`/`internal`) and `category` (`general`/`analytics`)
   decision — see the comments in `onboard.py` for why each of the 8
   tools here got the value it did.
4. **Shape the bots** — `create_bot_profile()` once per distinct audience.
   Suvidha has two: `external` (its own clients, on the `web-widget`
   channel, guarded so one client can never see another client's data,
   P&L detail, or ledger entries) and `internal` (Suvidha's own staff,
   on `slack`, sees everything).
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
`weave/packages/weave-sdk` and `weave/packages/shared-clients` as a
path dependency — see `initialize.sh` — the same way a real integrator
would pre-release; swap for `pip install weave-sdk` once it's published,
with zero other code changes) and weave's own stack already running
(`core` + Mongo/Redis/Qdrant, plus `mcp-gateway` — see `weave/PLAN.md`
and `weave/infra/`).

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
`onboard.py` just created:

```bash
cd ../weave/orchestrator
./.venv/Scripts/python.exe dev_cli.py \
  --tenant-id <tenant_id> --email owner@suvidha-finserve.test --password hunter2hunter2 \
  --channel web-widget "What's the status of invoice INV-2003?"
```

This exercises the exact `ChatStream` RPC a real `web-widget` channel
integration would call — dynamic tool discovery, the external
visibility filter, and guardrails all apply exactly as they would for a
real client.

## Config

| Env var | Default | Meaning |
|---|---|---|
| `DEMO_PORT` | `9102` | Port `api.py` listens on |
| `WEAVE_REPO` | `../weave` | Path to the sibling `weave/` checkout |
| `CORE_ADDR` | `localhost:9090` | `core`'s gRPC address |
| `DEMO_API_URL` | `http://localhost:9102` | Where `onboard.py` registers tools against |
| `DEMO_OWNER_EMAIL` / `DEMO_OWNER_PASSWORD` | `owner@suvidha-finserve.test` / `hunter2hunter2` | Owner account created in step 1 |
