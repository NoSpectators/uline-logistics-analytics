import sqlite3
import pandas as pd


DB_PATH = "logistics.db"


# ------------------------------------------------------------
# Connect to SQLite database
# ------------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


# ------------------------------------------------------------
# KPI 1: Overall Shipment Summary
# ------------------------------------------------------------
# Calculates:
# - total shipments
# - average delivery days
# - on-time delivery rate
# - delayed shipment count
#
# Stores results in:
# analytics_shipment_summary
# ------------------------------------------------------------
def generate_shipment_summary(conn):

    query = """
    SELECT
        COUNT(*) AS total_shipments,

        ROUND(AVG(delivery_days), 2) AS avg_delivery_days,

        SUM(CASE
            WHEN status = 'On-Time' THEN 1
            ELSE 0
        END) AS on_time_shipments,

        SUM(CASE
            WHEN status = 'Delayed' THEN 1
            ELSE 0
        END) AS delayed_shipments,

        ROUND(
            100.0 * SUM(CASE
                WHEN status = 'On-Time' THEN 1
                ELSE 0
            END) / COUNT(*),
            2
        ) AS on_time_delivery_rate

    FROM fact_shipments
    """

    df = pd.read_sql(query, conn)

    df.to_sql(
        "analytics_shipment_summary",
        conn,
        if_exists="replace",
        index=False
    )

    print("✔ analytics_shipment_summary created")


# ------------------------------------------------------------
# KPI 2: Carrier Performance Analysis
# ------------------------------------------------------------
# Calculates:
# - shipment volume by carrier
# - average delivery duration
# - delayed shipment percentage
#
# Stores results in:
# analytics_carrier_performance
# ------------------------------------------------------------
def generate_carrier_performance(conn):

    query = """
    SELECT
        carrier,

        COUNT(*) AS shipment_volume,

        ROUND(AVG(delivery_days), 2) AS avg_delivery_days,

        SUM(CASE
            WHEN status = 'Delayed' THEN 1
            ELSE 0
        END) AS delayed_shipments,

        ROUND(
            100.0 * SUM(CASE
                WHEN status = 'Delayed' THEN 1
                ELSE 0
            END) / COUNT(*),
            2
        ) AS delay_rate

    FROM fact_shipments
    GROUP BY carrier
    ORDER BY delay_rate DESC
    """

    df = pd.read_sql(query, conn)

    df.to_sql(
        "analytics_carrier_performance",
        conn,
        if_exists="replace",
        index=False
    )

    print("✔ analytics_carrier_performance created")


# ------------------------------------------------------------
# KPI 3: Warehouse Throughput
# ------------------------------------------------------------
# Calculates:
# - total shipments by warehouse
# - average delivery performance
#
# Stores results in:
# analytics_warehouse_throughput
# ------------------------------------------------------------
def generate_warehouse_throughput(conn):

    query = """
    SELECT
        warehouse_id,

        COUNT(*) AS total_shipments,

        ROUND(AVG(delivery_days), 2) AS avg_delivery_days

    FROM fact_shipments
    GROUP BY warehouse_id
    ORDER BY total_shipments DESC
    """

    df = pd.read_sql(query, conn)

    df.to_sql(
        "analytics_warehouse_throughput",
        conn,
        if_exists="replace",
        index=False
    )

    print("✔ analytics_warehouse_throughput created")


# ------------------------------------------------------------
# Main execution flow
# ------------------------------------------------------------
def main():

    conn = get_connection()

    print("Generating descriptive analytics tables...")

    generate_shipment_summary(conn)
    generate_carrier_performance(conn)
    generate_warehouse_throughput(conn)

    conn.close()

    print("✔ Descriptive analytics generation complete")


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    main()

