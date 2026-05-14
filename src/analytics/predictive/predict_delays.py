# src/analytics/predictive/predict_delays.py

import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

DB_PATH = "logistics.db"


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
def load_data(conn):
    return pd.read_sql("SELECT * FROM fact_shipments", conn)


# ------------------------------------------------------------
# Feature engineering (NO LEAKAGE VERSION)
# ------------------------------------------------------------
def prepare_features(df):
    df = df.copy()

    # --------------------------------------------------------
    # Target (what we want to predict)
    # --------------------------------------------------------
    y = df["status"].apply(lambda x: 1 if str(x).lower() == "delayed" else 0)

    # --------------------------------------------------------
    # Safe time-based features (order_date only)
    # --------------------------------------------------------
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["order_month"] = df["order_date"].dt.month
        df["order_weekday"] = df["order_date"].dt.weekday

    # --------------------------------------------------------
    # Drop ALL post-outcome / leakage columns
    # --------------------------------------------------------
    drop_cols = [
        "status",
        "ship_date",
        "delivery_date",
        "delivery_days"
    ]

    df = df.drop(columns=drop_cols, errors="ignore")

    # --------------------------------------------------------
    # Categorical encoding
    # --------------------------------------------------------
    cat_cols = [c for c in ["carrier", "warehouse_id"] if c in df.columns]
    df = pd.get_dummies(df, columns=cat_cols)

    X = df.select_dtypes(include=["number"])

    return X, y


# ------------------------------------------------------------
# Train model
# ------------------------------------------------------------
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print("\n📊 Model Evaluation (Leakage-Free):")
    print(classification_report(y_test, preds))

    return model


# ------------------------------------------------------------
# Save predictions
# ------------------------------------------------------------
def save_predictions(conn, df, model, X):
    df = df.copy()

    df["predicted_delay"] = model.predict(X)

    df.to_sql(
        "analytics_shipment_predictions",
        conn,
        if_exists="replace",
        index=False
    )

    print("✔ Saved analytics_shipment_predictions")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    conn = sqlite3.connect(DB_PATH)

    print("Loading data...")
    df = load_data(conn)

    print("Preparing leakage-free features...")
    X, y = prepare_features(df)

    print("Training model...")
    model = train_model(X, y)

    print("Saving predictions...")
    save_predictions(conn, df, model, X)

    conn.close()

    print("✔ Predictive pipeline complete (clean version)")


if __name__ == "__main__":
    main()

"""
After removing target leakage, I constrained the model to pre-outcome features only. 
The current feature set has limited predictive power in the synthetic dataset, which is expected. 
The goal of this stage was validating proper ML pipeline design rather than maximizing accuracy.

Preparing leakage-free features...
Training model...

📊 Model Evaluation (Leakage-Free):
              precision    recall  f1-score   support

           0       0.53      0.53      0.53       102
           1       0.51      0.51      0.51        98

    accuracy                           0.52       200
   macro avg       0.52      0.52      0.52       200
weighted avg       0.52      0.52      0.52       200

Saving predictions...
✔ Saved analytics_shipment_predictions
✔ Predictive pipeline complete (clean version)

"""