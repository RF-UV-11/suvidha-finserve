import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_gst_filing_status_found():
    resp = client.get("/gst-filings/GST-3001/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "filing_id": "GST-3001",
        "period": "2026-07",
        "return_type": "GSTR-3B",
        "status": "filed",
        "filed_on": "2026-08-18",
    }


def test_gst_filing_status_not_found():
    resp = client.get("/gst-filings/NOPE/status")
    assert resp.status_code == 404


def test_gst_filing_status_never_leaks_amount():
    resp = client.get("/gst-filings/GST-3001/status")
    assert "amount_inr" not in resp.json()


def test_invoice_status_found():
    resp = client.get("/invoices/INV-2003/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "overdue"
    assert body["amount_inr"] == 63750.00


def test_invoice_status_not_found():
    resp = client.get("/invoices/NOPE/status")
    assert resp.status_code == 404


def test_payroll_run_status_found():
    resp = client.get("/payroll-runs/PR-4001/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "processed"
    assert body["employee_count"] == 18


def test_payroll_run_status_never_leaks_total():
    resp = client.get("/payroll-runs/PR-4001/status")
    assert "total_inr" not in resp.json()


def test_internal_client_has_pii_and_gstin():
    resp = client.get("/internal/clients/client_meridian")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "rohan.kulkarni@meridiantextiles.example.test"
    assert body["gstin"] == "27AAECM5566K1Z2"


def test_internal_client_not_found():
    resp = client.get("/internal/clients/nope")
    assert resp.status_code == 404


def test_internal_financials_has_pl_detail():
    resp = client.get("/internal/clients/client_meridian/financials")
    assert resp.status_code == 200
    body = resp.json()
    assert body["revenue_inr"] == 4820000.00
    assert body["net_profit_inr"] == 1310000.00


def test_internal_ledger_entries():
    resp = client.get("/internal/clients/client_kaveri/ledger")
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_id"] == "client_kaveri"
    assert len(body["entries"]) == 2


def test_internal_ledger_not_found():
    resp = client.get("/internal/clients/nope/ledger")
    assert resp.status_code == 404


def test_revenue_report():
    resp = client.get("/internal/analytics/revenue?period=this_quarter")
    assert resp.status_code == 200
    body = resp.json()
    assert body["period"] == "this_quarter"
    assert body["clients_count"] == 3
    assert body["total_client_revenue_inr"] > 0
    assert body["top_client_by_revenue"] == "client_meridian"


def test_revenue_report_defaults_period():
    resp = client.get("/internal/analytics/revenue")
    assert resp.json()["period"] == "current"


def test_retention_report():
    resp = client.get("/internal/analytics/retention?period=this_quarter")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_clients"] == 3
    # client_meridian (since 2024-06-01) is the only one before 2025-01-01.
    assert body["clients_over_1yr"] == 1
    assert body["clients_under_1yr"] == 2
