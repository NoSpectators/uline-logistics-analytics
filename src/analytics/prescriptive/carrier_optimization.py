import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

DB_PATH = "logistics.db"


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
def load_data(conn):
    return pd.read_sql("SELECT * FROM fact_shipments", conn)


# ------------------------------------------------------------
# Train predictive model (leakage-free + engineered features)
# ------------------------------------------------------------
def train_model(df):
    df = df.copy()

    # target variable
    y = df["status"].apply(lambda x: 1 if str(x).lower() == "delayed" else 0)

    # safe time features (pre-outcome only)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.month
    df["order_weekday"] = df["order_date"].dt.weekday

    # engineered carrier prior signal (learned proxy risk)
    df["carrier_risk"] = df["carrier"].map({
        "UPS": 0.1,
        "FedEx": 0.2,
        "DHL": 0.38
    })

    # remove leakage columns
    df = df.drop(columns=[
        "status",
        "ship_date",
        "delivery_date",
        "delivery_days"
    ], errors="ignore")

    # one-hot encoding
    df = pd.get_dummies(df)

    X = df.select_dtypes(include=["number"])

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model, X.columns


# ------------------------------------------------------------
# Cost function (business objective)
# ------------------------------------------------------------
CARRIER_COST = {
    "UPS": 5.0,
    "FedEx": 7.0,
    "DHL": 9.0
}

DELAY_PENALTY = 50


def expected_cost(delay_prob, carrier):
    return (delay_prob * DELAY_PENALTY) + CARRIER_COST[carrier]


# ------------------------------------------------------------
# Prescriptive simulation engine
# ------------------------------------------------------------
def recommend_carrier(model, feature_cols, base_row):
    carriers = ["UPS", "FedEx", "DHL"]

    results = []

    for carrier in carriers:
        row = base_row.copy()
        row["carrier"] = carrier

        df = pd.DataFrame([row])

        # recompute safe time features
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["order_month"] = df["order_date"].dt.month
        df["order_weekday"] = df["order_date"].dt.weekday

        # recompute engineered risk feature (IMPORTANT)
        df["carrier_risk"] = df["carrier"].map({
            "UPS": 0.1,
            "FedEx": 0.2,
            "DHL": 0.38
        })

        # remove leakage fields
        df = df.drop(columns=[
            "status",
            "ship_date",
            "delivery_date",
            "delivery_days"
        ], errors="ignore")

        df = pd.get_dummies(df)

        # align with training features
        df = df.reindex(columns=feature_cols, fill_value=0)

        # predict probability of delay
        delay_prob = model.predict_proba(df)[0][1]

        # compute expected cost (optimization step)
        cost = expected_cost(delay_prob, carrier)

        results.append({
            "carrier": carrier,
            "delay_prob": delay_prob,
            "expected_cost": cost
        })

    # sort by best decision (min cost)
    results = sorted(results, key=lambda x: x["expected_cost"])

    return results


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    conn = sqlite3.connect(DB_PATH)

    print("Loading data...")
    df = load_data(conn)

    print("Training model...")
    model, feature_cols = train_model(df)

    sample = df.iloc[0].to_dict()

    print("\n📦 Prescriptive Optimization Results:\n")

    results = recommend_carrier(model, feature_cols, sample)

    for r in results:
        print(
            f"{r['carrier']}: "
            f"risk={r['delay_prob']:.3f}, "
            f"expected_cost={r['expected_cost']:.2f}"
        )

    print("\n✔ Best choice:", results[0]["carrier"])

    conn.close()


if __name__ == "__main__":
    main()