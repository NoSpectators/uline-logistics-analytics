import sqlite3
import pandas as pd

from src.analytics.descriptive.shipment_kpis import (
    generate_shipment_summary
)


# ------------------------------------------------------------
# Create temporary in-memory database
# ------------------------------------------------------------
def create_test_db():

    conn = sqlite3.connect(":memory:")

    sample_data = pd.DataFrame({
        "shipment_id": [1, 2, 3, 4],
        "carrier": ["UPS", "DHL", "FedEx", "UPS"],
        "warehouse_id": [1, 1, 2, 2],
        "delivery_days": [2, 5, 3, 4],
        "status": [
            "On-Time",
            "Delayed",
            "On-Time",
            "Delayed"
        ]
    })

    sample_data.to_sql(
        "fact_shipments",
        conn,
        index=False,
        if_exists="replace"
    )

    return conn


# ------------------------------------------------------------
# Test shipment summary generation
# ------------------------------------------------------------
def test_generate_shipment_summary():

    conn = create_test_db()

    generate_shipment_summary(conn)

    result = pd.read_sql(
        "SELECT * FROM analytics_shipment_summary",
        conn
    )

    # validate totals
    assert result["total_shipments"][0] == 4

    # validate delayed count
    assert result["delayed_shipments"][0] == 2

    # validate on-time rate
    assert result["on_time_delivery_rate"][0] == 50.0

    conn.close()