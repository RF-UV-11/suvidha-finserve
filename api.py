"""Suvidha FinServe — a fictional Indian accounting/bookkeeping firm's
real public-facing API, standing in for "a business that already runs
its own systems and wants Weave to reason over them without building an
MCP server." Every route here is a genuine HTTP endpoint a real firm
could run; onboard.py is what turns a subset of them into Weave tools
via the weave SDK's add_tool(), with visibility/category exactly as a
real integrator would set them.

This project is one of two independent, external reference projects
for weave/'s PLAN.md Phase 3.9 — it lives entirely outside the weave/
repo, exactly as a real tenant's integration would. Its sibling,
../tarang-electronics, is a retail-to-consumer (B2C) shape; this one is
deliberately B2B — Suvidha's "customers" are other businesses (its
bookkeeping/GST/payroll clients) checking on their own account, not
individual end consumers. See README.md for the full six-step
onboarding story.

Deliberate design choice for the visibility split: sensitive fields
(P&L detail, raw ledger entries, client contact PII) live only on
internal-only routes, never as extra fields on an external route's
response — the safest way to prevent a client-facing bot from ever
seeing another client's data, or a client's own staff-only detail.
"""

from fastapi import FastAPI, HTTPException

from data import (
    CLIENT_FINANCIALS,
    CLIENTS,
    GST_FILINGS,
    INVOICES,
    LEDGER_ENTRIES,
    PAYROLL_RUNS,
    client_retention_report,
    revenue_report,
)

app = FastAPI(title="Suvidha FinServe API", description="Indian accounting/bookkeeping firm — weave SDK reference integration")

# --------------------------------------------------------------------
# External / client-facing routes — safe to register as visibility=
# "external" tools. A client checking their own account never sees
# another client's data, P&L detail, or ledger entries below.
# --------------------------------------------------------------------


@app.get("/gst-filings/{filing_id}/status")
def get_gst_filing_status(filing_id: str):
    filing = GST_FILINGS.get(filing_id)
    if not filing:
        raise HTTPException(status_code=404, detail=f"no such GST filing {filing_id}")
    return {
        "filing_id": filing["filing_id"],
        "period": filing["period"],
        "return_type": filing["return_type"],
        "status": filing["status"],
        "filed_on": filing["filed_on"],
    }


@app.get("/invoices/{invoice_id}/status")
def get_invoice_status(invoice_id: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"no such invoice {invoice_id}")
    return {
        "invoice_id": invoice["invoice_id"],
        "amount_inr": invoice["amount_inr"],
        "status": invoice["status"],
        "due_date": invoice["due_date"],
    }


@app.get("/payroll-runs/{run_id}/status")
def get_payroll_run_status(run_id: str):
    run = PAYROLL_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"no such payroll run {run_id}")
    return {
        "run_id": run["run_id"],
        "period": run["period"],
        "status": run["status"],
        "employee_count": run["employee_count"],
    }


# --------------------------------------------------------------------
# Internal-only routes — visibility="internal" tools. Suvidha's own
# staff bot profile can use these; a client-facing external profile
# never sees them, at the tool-assembly stage, not via a guardrail
# catching it after the fact.
# --------------------------------------------------------------------


@app.get("/internal/clients/{client_id}")
def get_client_contact_details(client_id: str):
    client = CLIENTS.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"no such client {client_id}")
    return client


@app.get("/internal/clients/{client_id}/financials")
def get_client_financials(client_id: str):
    """P&L-style detail — revenue, expenses, net profit — never exposed
    on any external route."""
    financials = CLIENT_FINANCIALS.get(client_id)
    if not financials:
        raise HTTPException(status_code=404, detail=f"no financial record for client {client_id}")
    return financials


@app.get("/internal/clients/{client_id}/ledger")
def get_ledger_entries(client_id: str):
    entries = LEDGER_ENTRIES.get(client_id)
    if entries is None:
        raise HTTPException(status_code=404, detail=f"no ledger entries for client {client_id}")
    return {"client_id": client_id, "entries": entries}


@app.get("/internal/analytics/revenue")
def get_revenue_report(period: str = "current"):
    return revenue_report(period)


@app.get("/internal/analytics/retention")
def get_client_retention_report(period: str = "current"):
    return client_retention_report(period)


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("DEMO_PORT", "9102")))
