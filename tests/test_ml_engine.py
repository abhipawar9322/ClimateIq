"""
Unit tests for Machine Learning Predictive Risk Engine.
"""

import pytest
import pandas as pd
from src.ml_engine import (
    generate_training_data,
    build_and_train_pipeline,
    predict_single_facility,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES
)


def test_generate_training_data():
    df = generate_training_data(n_samples=150, random_state=42)
    assert len(df) == 150
    assert "loss_ratio_pct" in df.columns
    for feat in NUMERIC_FEATURES + CATEGORICAL_FEATURES:
        assert feat in df.columns
    assert df["loss_ratio_pct"].min() > 0.0


def test_build_and_train_pipeline():
    df = generate_training_data(n_samples=200, random_state=42)
    pipeline, metrics = build_and_train_pipeline(
        df, n_estimators=25, max_depth=6, test_size=0.25, random_state=42
    )
    
    assert pipeline is not None
    assert metrics["r2_test"] > 0.60
    assert metrics["rmse_test"] > 0.0
    assert len(metrics["feature_importances"]) > 0


def test_predict_single_facility():
    df = generate_training_data(n_samples=100, random_state=42)
    pipeline, _ = build_and_train_pipeline(df, n_estimators=20, max_depth=5)
    
    sample_feat = {
        "elevation_m": 12.0,
        "distance_to_coast_km": 5.0,
        "climate_zone": "Tropical",
        "sector": "Data Centers & IT Infrastructure",
        "flood_hazard": 80.0,
        "heat_hazard": 75.0,
        "drought_hazard": 30.0,
        "wildfire_hazard": 20.0,
        "rainfall_hazard": 85.0,
        "asset_value_m": 450.0,
        "employees": 600,
        "backup_power": 1,
        "flood_barrier": 1,
        "water_recycling": 1
    }
    
    res = predict_single_facility(pipeline, sample_feat)
    assert "predicted_loss_ratio_pct" in res
    assert "predicted_dollar_loss_m" in res
    assert res["predicted_loss_ratio_pct"] > 0.0
    assert res["predicted_dollar_loss_m"] > 0.0
