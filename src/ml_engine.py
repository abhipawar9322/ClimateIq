"""
Machine Learning Predictive Risk Engine for ClimateIQ.
Uses Scikit-Learn to train and deploy a Random Forest Regressor predicting
the Climate Loss Ratio (%) and Financial Vulnerability of enterprise facilities.
Provides model evaluation metrics (R2, RMSE, MAE), feature importances, and interactive inference.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from src.data_loader import DATA_DIR, load_locations_data, LOCATIONS_SEED

MODEL_PATH = DATA_DIR / "trained_model.joblib"
METRICS_PATH = DATA_DIR / "model_metrics.joblib"

NUMERIC_FEATURES = [
    "elevation_m",
    "distance_to_coast_km",
    "flood_hazard",
    "heat_hazard",
    "drought_hazard",
    "wildfire_hazard",
    "rainfall_hazard",
    "asset_value_m",
    "employees",
    "backup_power",
    "flood_barrier",
    "water_recycling",
]

CATEGORICAL_FEATURES = [
    "sector",
    "climate_zone"
]


def generate_training_data(n_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    """
    Generates an empirical multi-hazard climate impact training benchmark
    covering diverse global regions, extreme hazard conditions, and structural defenses.
    """
    rng = np.random.default_rng(random_state)
    
    sectors = [
        "Data Centers & IT Infrastructure",
        "Manufacturing & Heavy Industrial",
        "Agriculture & Food Supply",
        "Logistics, Ports & Warehousing",
        "Commercial Real Estate & Hospitality",
        "Renewable Energy & Utilities"
    ]
    climate_zones = ["Tropical", "Subtropical", "Temperate", "Arid", "Mediterranean", "Continental"]
    
    # Base cities lookup
    cities_pool = [
        {"city": r[0], "elev": r[4], "coast": r[5], "zone": r[11], "fl": r[6], "ht": r[7], "dr": r[8], "wf": r[9], "rf": r[10]}
        for r in LOCATIONS_SEED
    ]
    
    rows = []
    for _ in range(n_samples):
        base_city = rng.choice(cities_pool)
        sector = rng.choice(sectors)
        
        # Introduce stochastic variation around location baseline
        elevation = max(0, base_city["elev"] + rng.normal(0, 15))
        dist_coast = max(0.5, base_city["coast"] + rng.normal(0, 10))
        zone = base_city["zone"]
        
        flood = np.clip(base_city["fl"] + rng.normal(0, 12), 5, 100)
        heat = np.clip(base_city["ht"] + rng.normal(0, 10), 5, 100)
        drought = np.clip(base_city["dr"] + rng.normal(0, 12), 5, 100)
        wildfire = np.clip(base_city["wf"] + rng.normal(0, 14), 5, 100)
        rainfall = np.clip(base_city["rf"] + rng.normal(0, 10), 5, 100)
        
        asset_val = np.round(rng.uniform(50, 950), 1)
        employees = int(rng.uniform(50, 3500))
        
        backup_power = int(rng.choice([0, 1], p=[0.35, 0.65]))
        flood_barrier = int(rng.choice([0, 1], p=[0.60, 0.40]))
        water_recycling = int(rng.choice([0, 1], p=[0.55, 0.45]))
        
        # Sector vulnerability weights
        sector_factor = {
            "Data Centers & IT Infrastructure": 1.15,
            "Manufacturing & Heavy Industrial": 1.25,
            "Agriculture & Food Supply": 1.35,
            "Logistics, Ports & Warehousing": 1.20,
            "Commercial Real Estate & Hospitality": 0.95,
            "Renewable Energy & Utilities": 1.10
        }[sector]
        
        # Signal: realistic climate loss ratio scale (1.0% to 14.0%)
        norm_flood = (flood * 0.35 + rainfall * 0.25) * (1.0 / (1.0 + 0.008 * dist_coast))
        norm_heat_fire = (heat * 0.25 + wildfire * 0.25)
        norm_drought = drought * 0.15
        composite_hazard = np.clip(norm_flood + norm_heat_fire + norm_drought, 5.0, 100.0)
        
        # Mitigation defense damping (up to 55% reduction)
        mitigation_discount = (
            (0.25 if flood_barrier else 0.0) +
            (0.18 if backup_power else 0.0) +
            (0.12 if water_recycling else 0.0)
        )
        
        # Non-linear loss ratio curve
        base_signal = 1.2 + 9.5 * ((composite_hazard / 100.0) ** 1.7) * sector_factor
        loss_ratio = base_signal * (1.0 - mitigation_discount)
        # Add realistic empirical observation noise
        loss_ratio += rng.normal(0, 0.20)
        loss_ratio = float(np.clip(loss_ratio, 0.20, 15.0))
        
        rows.append({
            "elevation_m": elevation,
            "distance_to_coast_km": dist_coast,
            "climate_zone": zone,
            "sector": sector,
            "flood_hazard": flood,
            "heat_hazard": heat,
            "drought_hazard": drought,
            "wildfire_hazard": wildfire,
            "rainfall_hazard": rainfall,
            "asset_value_m": asset_val,
            "employees": employees,
            "backup_power": backup_power,
            "flood_barrier": flood_barrier,
            "water_recycling": water_recycling,
            "loss_ratio_pct": round(loss_ratio, 2)
        })
        
    return pd.DataFrame(rows)


def build_and_train_pipeline(
    df: pd.DataFrame,
    n_estimators: int = 120,
    max_depth: Optional[int] = 12,
    test_size: float = 0.20,
    random_state: int = 42
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Constructs, trains, and validates the Scikit-Learn Machine Learning Pipeline.
    """
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["loss_ratio_pct"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )
    
    # Model
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=1
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model)
    ])
    
    # Train
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = float(r2_score(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    
    # Cross validation (3-fold for speed during runtime)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=3, scoring="r2")
    cv_mean = float(np.mean(cv_scores))
    cv_std = float(np.std(cv_scores))
    
    # Extract Feature Importances
    ohe_cols = pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = NUMERIC_FEATURES + list(ohe_cols)
    importances = pipeline.named_steps["regressor"].feature_importances_
    
    feat_imp = sorted(
        zip(all_feature_names, importances),
        key=lambda x: x[1],
        reverse=True
    )
    
    metrics = {
        "r2_test": round(r2, 4),
        "rmse_test": round(rmse, 4),
        "mae_test": round(mae, 4),
        "cv_r2_mean": round(cv_mean, 4),
        "cv_r2_std": round(cv_std, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importances": feat_imp,
        "y_test_sample": y_test.iloc[:50].tolist(),
        "y_pred_sample": [round(val, 2) for val in y_pred[:50].tolist()]
    }
    
    return pipeline, metrics


def get_trained_model(force_retrain: bool = False, n_estimators: int = 120, max_depth: int = 12) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Loads saved model from disk or trains a fresh pipeline and caches it.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not force_retrain and MODEL_PATH.exists() and METRICS_PATH.exists():
        try:
            pipeline = joblib.load(MODEL_PATH)
            metrics = joblib.load(METRICS_PATH)
            return pipeline, metrics
        except Exception:
            pass  # Fall back to training
            
    # Train
    df_train = generate_training_data(n_samples=1200)
    pipeline, metrics = build_and_train_pipeline(
        df_train,
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    
    # Persist
    joblib.dump(pipeline, MODEL_PATH)
    joblib.dump(metrics, METRICS_PATH)
    return pipeline, metrics


def predict_single_facility(
    pipeline: Pipeline,
    feature_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs inference for an individual facility feature payload.
    """
    df_input = pd.DataFrame([feature_dict])
    pred_loss_ratio = float(pipeline.predict(df_input)[0])
    pred_loss_ratio = max(0.05, round(pred_loss_ratio, 2))
    
    asset_val = float(feature_dict.get("asset_value_m", 100.0))
    pred_dollar_loss_m = round(asset_val * (pred_loss_ratio / 100.0), 2)
    
    return {
        "predicted_loss_ratio_pct": pred_loss_ratio,
        "predicted_dollar_loss_m": pred_dollar_loss_m,
    }
