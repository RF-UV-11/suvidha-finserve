"""onboard.py — the actual tutorial for integrating `weave` into an
existing business. Read this file top to bottom to learn how to wire
your own systems into Weave; each STEP below narrates one stage of the
real onboarding sequence a business goes through, in the order they'd
actually do it. This is not a toy — every RPC/SDK call here is exactly
what a real integrator would run, just against a fictional business
(Suvidha FinServe, an Indian accounting/bookkeeping firm) and a
fictional dataset (data.py/api.py).

This project's sibling, ../tarang-electronics, walks the same six steps
for a B2C retailer; this one deliberately demonstrates a B2B shape —
Suvidha's "customers" are its own bookkeeping/GST/payroll clients
checking their own account, not individual consumers.

Prerequisites (see README.md for the full walkthrough):
  1. weave/'s own stack is running: `core` (CORE_ADDR, default
     localhost:9090) reachable, with Mongo/Redis/Qdrant behind it.
  2. This project's own API is running (DEMO_API_URL, default
     http://localhost:9102) — that's api.py, started by initialize.sh.
  3. The `weave` SDK is installed from weave/'s packages/weave-sdk (see
     initialize.sh / pyproject.toml) — this project never vendors or
     copies weave's code, it depends on it like any external consumer
     would.

Usage:
    ./.venv/Scripts/python.exe onboard.py

Idempotency: none — re-running creates a second tenant with a fresh
random suffix each time. This is an onboarding walkthrough, not a
migration; delete the tenant via core if you need to start over.
"""

import asyncio
import os
import secrets

from weave_shared_clients import CoreClient

from core.data_access.v1 import auth_pb2, tenant_pb2

import weave

CORE_ADDR = os.environ.get("CORE_ADDR", "localhost:9090")
DEMO_API_URL = os.environ.get("DEMO_API_URL", "http://localhost:9102")
OWNER_EMAIL = os.environ.get("DEMO_OWNER_EMAIL", "owner@suvidha-finserve.test")
OWNER_PASSWORD = os.environ.get("DEMO_OWNER_PASSWORD", "hunter2hunter2")


async def _step1_sign_up_and_step2_authenticate() -> tuple[str, str]:
    """STEP 1 — Sign up: CreateTenant + Register (an owner account).
    STEP 2 — Authenticate: Login -> JWT.

    CreateTenant/Register are core's real public bootstrap RPCs,
    unauthenticated by design for exactly this reason (there's no token
    to present before a tenant/user exists at all) — not a special-cased
    dev shortcut. Every real integration starts here, exactly like this."""
    core = CoreClient(CORE_ADDR)
    try:
        print("STEP 1: signing up — CreateTenant + Register(owner)")
        tenant_resp = await core.tenant.CreateTenant(
            tenant_pb2.CreateTenantRequest(
                display_name=f"Suvidha FinServe ({secrets.token_hex(3)})",
                tenant_type="business",
            )
        )
        tenant_id = tenant_resp.tenant._id
        await core.auth.Register(
            auth_pb2.RegisterRequest(
                tenant_id=tenant_id, email=OWNER_EMAIL, password=OWNER_PASSWORD, role=1  # owner
            )
        )
        print(f"   -> tenant_id={tenant_id}")

        print("STEP 2: authenticating — Login")
        login_resp = await core.auth.Login(
            auth_pb2.LoginRequest(tenant_id=tenant_id, email=OWNER_EMAIL, password=OWNER_PASSWORD)
        )
        print("   -> got access token (JWT)")
        return tenant_id, login_resp.access_token
    finally:
        await core.close()


async def main() -> None:
    tenant_id, _access_token = await _step1_sign_up_and_step2_authenticate()

    # weave.connect_async() re-authenticates internally (any real
    # integrator would just call this directly rather than logging in
    # twice) — the explicit Login above exists only to narrate STEP 2 as
    # its own visible stage.
    client = await weave.connect_async(
        tenant_id=tenant_id, email=OWNER_EMAIL, password=OWNER_PASSWORD, core_addr=CORE_ADDR
    )
    try:
        print()
        print("STEP 3: describing the business's systems — weave.connect() + add_tool()")
        print("        (each tool's visibility/category is a deliberate decision, not left default)")

        # --- External tools: safe for a client-facing bot --------------
        await client.add_tool(
            name="check_gst_filing_status",
            description=(
                "Check the status (filed/pending/late) and filing date of a GST return, given the filing ID "
                "(e.g. GST-3001)."
            ),
            endpoint=f"{DEMO_API_URL}/gst-filings/{{filing_id}}/status",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"filing_id": {"type": "string", "description": "The GST filing ID, e.g. GST-3001."}},
                "required": ["filing_id"],
            },
            visibility="external",
            category="general",
        )
        await client.add_tool(
            name="get_invoice_status",
            description="Look up an invoice's amount (INR), payment status, and due date, given the invoice ID.",
            endpoint=f"{DEMO_API_URL}/invoices/{{invoice_id}}/status",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"invoice_id": {"type": "string", "description": "The invoice ID, e.g. INV-2001."}},
                "required": ["invoice_id"],
            },
            visibility="external",
            category="general",
        )
        await client.add_tool(
            name="get_payroll_run_status",
            description="Check whether a payroll run has been processed, given the run ID.",
            endpoint=f"{DEMO_API_URL}/payroll-runs/{{run_id}}/status",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"run_id": {"type": "string", "description": "The payroll run ID, e.g. PR-4001."}},
                "required": ["run_id"],
            },
            visibility="external",
            category="general",
        )

        # --- Internal-only tools: Suvidha's own staff only -------------
        await client.add_tool(
            name="get_client_contact_details",
            description=(
                "Look up a client company's contact details (contact person, email, phone, address, GSTIN) by "
                "client ID. Contains PII — internal/staff use only."
            ),
            endpoint=f"{DEMO_API_URL}/internal/clients/{{client_id}}",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"client_id": {"type": "string", "description": "The client ID, e.g. client_meridian."}},
                "required": ["client_id"],
            },
            visibility="internal",
            category="general",
        )
        await client.add_tool(
            name="get_client_financials",
            description=(
                "Get a client's P&L-style detail (revenue, expenses, net profit) for the current period. "
                "Internal/staff use only, never expose one client's financials to another client."
            ),
            endpoint=f"{DEMO_API_URL}/internal/clients/{{client_id}}/financials",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"client_id": {"type": "string", "description": "The client ID, e.g. client_meridian."}},
                "required": ["client_id"],
            },
            visibility="internal",
            category="general",
        )
        await client.add_tool(
            name="get_ledger_entries",
            description="List raw ledger/expense entries for a client. Internal/staff use only.",
            endpoint=f"{DEMO_API_URL}/internal/clients/{{client_id}}/ledger",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"client_id": {"type": "string", "description": "The client ID, e.g. client_meridian."}},
                "required": ["client_id"],
            },
            visibility="internal",
            category="general",
        )
        await client.add_tool(
            name="get_revenue_report",
            description=(
                "Get an aggregate firm-wide revenue report across all clients: total client revenue, net profit, "
                "and the top client by revenue for a given period. Internal/staff use only."
            ),
            endpoint=f"{DEMO_API_URL}/internal/analytics/revenue",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"period": {"type": "string", "description": "Reporting period, e.g. 'this_quarter'."}},
            },
            visibility="internal",
            category="analytics",
        )
        await client.add_tool(
            name="get_client_retention_report",
            description=(
                "Get an aggregate client-retention report: how many clients have been with the firm over vs. "
                "under a year, for a given period. Internal/staff use only."
            ),
            endpoint=f"{DEMO_API_URL}/internal/analytics/retention",
            method="GET",
            params_schema={
                "type": "object",
                "properties": {"period": {"type": "string", "description": "Reporting period, e.g. 'this_quarter'."}},
            },
            visibility="internal",
            category="analytics",
        )
        print("   -> registered 8 tools (3 external, 5 internal)")

        print()
        print("STEP 4: shaping the bots — create_bot_profile() per audience")
        external_profile = await client.create_bot_profile(
            name="external",
            persona="personas/external.md",
            channels=["web-widget"],
            roles_allowed=["customer"],
            visibility="external",
            guardrails=[
                "Never disclose one client's data to a different client.",
                "Never disclose P&L detail, ledger entries, or another client's contact information.",
                "Only answer questions about the requesting client's own filings, invoices, and payroll.",
            ],
            web_search_enabled=True,
        )
        internal_profile = await client.create_bot_profile(
            name="internal",
            persona="personas/internal.md",
            channels=["slack"],
            roles_allowed=["staff", "admin", "owner"],
            visibility="internal",
            web_search_enabled=False,
        )
        print(f"   -> external profile: {external_profile.id} (channel web-widget, guardrails on)")
        print(f"   -> internal profile: {internal_profile.id} (channel slack, sees all 8 tools)")

        print()
        print("STEP 5: connect a channel — the step this walkthrough stops short of.")
        print("        A real deployment embeds web/'s chat widget on suvidha-finserve.example")
        print("        pointed at the external profile's web-widget channel, and/or wires a Slack")
        print("        app pointed at the internal profile's slack channel. See README.md.")
        print()
        print("STEP 6: go live — once a channel is connected, end users (Suvidha's own clients")
        print("        or staff) interact through it. Until then, weave/'s own orchestrator/dev_cli.py")
        print("        exercises the exact same ChatStream RPC a real channel integration would call")
        print("        (see README.md for the exact command against this tenant).")
        print()
        print(f"tenant_id={tenant_id}")
        print(f"owner_email={OWNER_EMAIL}")
        print(f"owner_password={OWNER_PASSWORD}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
