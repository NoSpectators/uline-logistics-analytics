import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

DB_PATH = "logistics.db"


def generate_orders(n=1000):
    np.random.seed(42)

    orders = pd.DataFrame({
        "order_id": range(1, n + 1),
        "customer_id": np.random.randint(1000, 2000, n),
        "order_date": [
            datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 90))
            for _ in range(n)
        ],
        "warehouse_id": np.random.choice([1, 2, 3], n),
        "total_weight": np.round(np.random.uniform(5, 100, n), 2)
    })

    return orders


def generate_shipments(orders):
    n = len(orders)

    shipments = pd.DataFrame({
        "shipment_id": range(1, n + 1),
        "order_id": orders["order_id"],
        "carrier": np.random.choice(["UPS", "FedEx", "DHL"], n),
        "ship_date": orders["order_date"] + pd.to_timedelta(
            np.random.randint(1, 3, n), unit="d"
        ),
    })

    shipments["delivery_date"] = shipments["ship_date"] + pd.to_timedelta(
        np.random.randint(1, 7, n), unit="d"
    )

    shipments["status"] = np.where(
        (shipments["delivery_date"] - shipments["ship_date"]).dt.days > 3,
        "Delayed",
        "On-Time"
    )

    return shipments


def load_to_sqlite(orders, shipments):
    conn = sqlite3.connect(DB_PATH)

    orders.to_sql("orders", conn, if_exists="replace", index=False)
    shipments.to_sql("shipments", conn, if_exists="replace", index=False)

    conn.close()


def generate_data():
    orders = generate_orders()
    shipments = generate_shipments(orders)
    load_to_sqlite(orders, shipments)

    print("✅ Data generated and loaded into SQLite")


if __name__ == "__main__":
    generate_data()