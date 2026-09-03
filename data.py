"""In-memory canned data for Suvidha FinServe — a fictional Indian
accounting/bookkeeping firm offering GST filing, invoicing, and payroll
services to small/medium businesses. Used to demonstrate integrating
the `weave` SDK (see README.md for the full six-step walkthrough).

Not a real business system: a fixed, restart-empty dataset just
realistic enough to demonstrate the external/internal tool-visibility
split and give the analytics endpoints something non-trivial to
aggregate over. Unlike Tarang Electronics (../tarang-electronics, the
sibling reference project), Suvidha's "customers" are other businesses
(B2B), not individual consumers — a deliberately different shape.
"""

from datetime import date

CLIENTS: dict[str, dict] = {
    "client_meridian": {
        "client_id": "client_meridian", "name": "Meridian Textiles Pvt Ltd",
        "contact_person": "Rohan Kulkarni", "email": "rohan.kulkarni@meridiantextiles.example.test",
        "phone": "+91-98220-55671", "address": "Plot 44, MIDC Industrial Area, Nashik, Maharashtra 422010",
        "gstin": "27AAECM5566K1Z2", "since": "2024-06-01",
    },
    "client_kaveri": {
        "client_id": "client_kaveri", "name": "Kaveri Foods LLP",
        "contact_person": "Lakshmi Iyer", "email": "lakshmi.iyer@kaverifoods.example.test",
        "phone": "+91-94480-22187", "address": "12 Anna Salai, Chennai, Tamil Nadu 600002",
        "gstin": "33AAFCK7788L1Z9", "since": "2025-01-15",
    },
    "client_bhavani": {
        "client_id": "client_bhavani", "name": "Bhavani Logistics Pvt Ltd",
        "contact_person": "Suresh Naidu", "email": "suresh.naidu@bhavanilogistics.example.test",
        "phone": "+91-99490-33456", "address": "6-3-1187, Begumpet, Hyderabad, Telangana 500016",
        "gstin": "36AABCB4321M1Z5", "since": "2025-09-20",
    },
}

INVOICES: dict[str, dict] = {
    "INV-2001": {
        "invoice_id": "INV-2001", "client_id": "client_meridian", "amount_inr": 84500.00,
        "status": "paid", "issued_on": "2026-08-01", "due_date": "2026-08-15",
    },
    "INV-2002": {
        "invoice_id": "INV-2002", "client_id": "client_kaveri", "amount_inr": 42000.00,
        "status": "pending", "issued_on": "2026-08-20", "due_date": "2026-09-05",
    },
    "INV-2003": {
        "invoice_id": "INV-2003", "client_id": "client_bhavani", "amount_inr": 63750.00,
        "status": "overdue", "issued_on": "2026-07-10", "due_date": "2026-07-25",
    },
    "INV-2004": {
        "invoice_id": "INV-2004", "client_id": "client_meridian", "amount_inr": 91200.00,
        "status": "pending", "issued_on": "2026-08-28", "due_date": "2026-09-12",
    },
}

GST_FILINGS: dict[str, dict] = {
    "GST-3001": {
        "filing_id": "GST-3001", "client_id": "client_meridian", "period": "2026-07",
        "return_type": "GSTR-3B", "status": "filed", "amount_inr": 118200.00, "filed_on": "2026-08-18",
    },
    "GST-3002": {
        "filing_id": "GST-3002", "client_id": "client_kaveri", "period": "2026-07",
        "return_type": "GSTR-3B", "status": "filed", "amount_inr": 56400.00, "filed_on": "2026-08-19",
    },
    "GST-3003": {
        "filing_id": "GST-3003", "client_id": "client_bhavani", "period": "2026-07",
        "return_type": "GSTR-3B", "status": "late", "amount_inr": 73900.00, "filed_on": "2026-08-25",
    },
    "GST-3004": {
        "filing_id": "GST-3004", "client_id": "client_meridian", "period": "2026-08",
        "return_type": "GSTR-3B", "status": "pending", "amount_inr": None, "filed_on": None,
    },
}

PAYROLL_RUNS: dict[str, dict] = {
    "PR-4001": {
        "run_id": "PR-4001", "client_id": "client_meridian", "period": "2026-08",
        "status": "processed", "total_inr": 612000.00, "employee_count": 18,
    },
    "PR-4002": {
        "run_id": "PR-4002", "client_id": "client_kaveri", "period": "2026-08",
        "status": "processed", "total_inr": 284000.00, "employee_count": 9,
    },
    "PR-4003": {
        "run_id": "PR-4003", "client_id": "client_bhavani", "period": "2026-08",
        "status": "pending", "total_inr": None, "employee_count": 27,
    },
}

# Internal-only: P&L-style financial detail per client.
CLIENT_FINANCIALS: dict[str, dict] = {
    "client_meridian": {
        "client_id": "client_meridian", "period": "2026-Q2", "revenue_inr": 4820000.00,
        "expenses_inr": 3510000.00, "net_profit_inr": 1310000.00,
    },
    "client_kaveri": {
        "client_id": "client_kaveri", "period": "2026-Q2", "revenue_inr": 1960000.00,
        "expenses_inr": 1640000.00, "net_profit_inr": 320000.00,
    },
    "client_bhavani": {
        "client_id": "client_bhavani", "period": "2026-Q2", "revenue_inr": 2740000.00,
        "expenses_inr": 2415000.00, "net_profit_inr": 325000.00,
    },
}

# Internal-only: raw ledger/expense entries per client.
LEDGER_ENTRIES: dict[str, list[dict]] = {
    "client_meridian": [
        {"entry_id": "LE-1", "date": "2026-08-02", "category": "raw_materials", "type": "debit", "amount_inr": 215000.00},
        {"entry_id": "LE-2", "date": "2026-08-10", "category": "sales", "type": "credit", "amount_inr": 480000.00},
        {"entry_id": "LE-3", "date": "2026-08-22", "category": "payroll", "type": "debit", "amount_inr": 612000.00},
    ],
    "client_kaveri": [
        {"entry_id": "LE-4", "date": "2026-08-05", "category": "sales", "type": "credit", "amount_inr": 195000.00},
        {"entry_id": "LE-5", "date": "2026-08-19", "category": "logistics", "type": "debit", "amount_inr": 41000.00},
    ],
    "client_bhavani": [
        {"entry_id": "LE-6", "date": "2026-08-08", "category": "fuel", "type": "debit", "amount_inr": 88000.00},
        {"entry_id": "LE-7", "date": "2026-08-15", "category": "sales", "type": "credit", "amount_inr": 260000.00},
    ],
}


def revenue_report(period: str) -> dict:
    """Aggregates CLIENT_FINANCIALS into a firm-wide revenue report.
    period is accepted but not actually used to filter this fixed
    dataset — it's part of the tool's schema so the shape matches what a
    real analytics endpoint would take, same convention as the sibling
    tarang-electronics reference project."""
    total_revenue = sum(c["revenue_inr"] for c in CLIENT_FINANCIALS.values())
    total_profit = sum(c["net_profit_inr"] for c in CLIENT_FINANCIALS.values())
    top_client = max(CLIENT_FINANCIALS.values(), key=lambda c: c["revenue_inr"])
    return {
        "period": period,
        "clients_count": len(CLIENT_FINANCIALS),
        "total_client_revenue_inr": round(total_revenue, 2),
        "total_client_net_profit_inr": round(total_profit, 2),
        "top_client_by_revenue": top_client["client_id"],
        "generated_on": date.today().isoformat(),
    }


def client_retention_report(period: str) -> dict:
    """Aggregates CLIENTS by tenure into a retention report, same
    period-is-schema-only caveat as revenue_report."""
    long_tenure = sum(1 for c in CLIENTS.values() if c["since"] < "2025-01-01")
    return {
        "period": period,
        "total_clients": len(CLIENTS),
        "clients_over_1yr": long_tenure,
        "clients_under_1yr": len(CLIENTS) - long_tenure,
        "generated_on": date.today().isoformat(),
    }
