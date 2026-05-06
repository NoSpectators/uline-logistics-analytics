import sqlite3
import os

DB_PATH = "logistics.db"


def run_sql_file(cursor, filepath):
    with open(filepath, "r") as f:
        sql = f.read()
    cursor.executescript(sql)


def run_transformations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    base_path = "sql"

    # Run staging
    run_sql_file(cursor, os.path.join(base_path, "staging", "stg_shipments.sql"))

    # Run marts
    run_sql_file(cursor, os.path.join(base_path, "marts", "fact_shipments.sql"))
    run_sql_file(cursor, os.path.join(base_path, "marts", "dim_carrier.sql"))

    conn.commit()
    conn.close()

    print("✅ Transformations complete")


if __name__ == "__main__":
    run_transformations()