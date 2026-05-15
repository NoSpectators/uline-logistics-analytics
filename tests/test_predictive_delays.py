import pandas as pd

from src.analytics.predictive.predict_delays import (
    prepare_features,
    train_model
)


# ------------------------------------------------------------
# Fake dataset matching fact_shipments schema
# ------------------------------------------------------------
def create_test_data():

    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5],
        "order_date": pd.date_range("2025-01-01", periods=5),
        "warehouse_id": [1, 1, 2, 2, 3],
        "total_weight": [10, 20, 15, 30, 25],
        "shipment_id": [101, 102, 103, 104, 105],
        "carrier": ["UPS", "FedEx", "DHL", "UPS", "FedEx"],
        "ship_date": pd.date_range("2025-01-02", periods=5),
        "delivery_date": pd.date_range("2025-01-05", periods=5),
        "status": ["On-Time", "Delayed", "On-Time", "Delayed", "On-Time"],
        "delivery_days": [3, 5, 2, 4, 3]
    })


# ------------------------------------------------------------
# Test feature engineering (most important part)
# ------------------------------------------------------------
def test_prepare_features_outputs_valid_data():

    df = create_test_data()

    X, y = prepare_features(df)

    # must return something usable for ML
    assert len(X) == len(y)

    # no leakage columns should remain
    assert "delivery_days" not in X.columns
    assert "ship_date" not in X.columns
    assert "delivery_date" not in X.columns
    assert "status" not in X.columns


# ------------------------------------------------------------
# Test model training works
# ------------------------------------------------------------
def test_model_training_runs():

    df = create_test_data()

    X, y = prepare_features(df)

    model = train_model(X, y)

    assert model is not None

    # ensure model can predict
    preds = model.predict(X)

    assert len(preds) == len(X)