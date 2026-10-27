"""
Predictive ML Engine Page — ClimateIQ.
Implements, evaluates, and deploys a Scikit-Learn Random Forest Pipeline
to predict corporate climate financial loss ratios (%) and physical vulnerability.
"""

import streamlit as st
import pandas as pd
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.ml_engine import (
    get_trained_model,
    predict_single_facility,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES
)
from src.visuals import (
    create_feature_importance_plot,
    create_model_residuals_plot
)
from src.config import THEME_COLORS

st.set_page_config(page_title="Predictive ML Engine | ClimateIQ", page_icon="🤖", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Predictive Machine Learning Risk Engine",
    subtitle="Supervised Scikit-Learn regression pipeline predicting corporate climate loss ratios (%) and feature importance attribution.",
    icon="🤖"
)

# Load trained model & metrics
with st.spinner("Loading Scikit-Learn predictive model..."):
    pipeline, metrics = get_trained_model(force_retrain=False)

# Model Architecture Callout
st.markdown(
    """
    <div class="metric-card" style="border-left: 6px solid #2A9D8F; background: #F8FBF9;">
        <div style="font-weight: 700; font-size: 1.05rem; color: #0F4C3A; margin-bottom: 4px;">Scikit-Learn Regression Pipeline Architecture</div>
        <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
            <code>ColumnTransformer(StandardScaler(numeric) + OneHotEncoder(categorical)) → RandomForestRegressor</code>
            <br>Trained on multi-hazard empirical benchmarks across 6 global climate zones and 6 industrial sectors to predict <b>Loss Ratio (% of total asset value)</b>.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Metric KPI Cards
st.markdown("### 📈 Live Model Performance & Validation Metrics")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    render_metric_card("Test R² Score", f"{metrics['r2_test']:.3f}", "Out-of-sample goodness-of-fit", delta_color="#2A9D8F")
with kpi2:
    render_metric_card("Cross-Validation R²", f"{metrics['cv_r2_mean']:.3f}", f"± {metrics['cv_r2_std']:.3f} (3-Fold CV)")
with kpi3:
    render_metric_card("Root Mean Sq Error (RMSE)", f"{metrics['rmse_test']:.3f}%", "Loss ratio standard deviation")
with kpi4:
    render_metric_card("Mean Abs Error (MAE)", f"{metrics['mae_test']:.3f}%", f"Train: {metrics['train_samples']} | Test: {metrics['test_samples']}")

# Diagnostics Charts: Feature Importance + Residuals
c_imp, c_res = st.columns([1.1, 1])

with c_imp:
    st.plotly_chart(
        create_feature_importance_plot(metrics["feature_importances"], top_n=10),
        use_container_width=True
    )

with c_res:
    y_test_sub = metrics.get("y_test_sample", [])
    y_pred_sub = metrics.get("y_pred_sample", [])
    if y_test_sub and y_pred_sub:
        st.plotly_chart(
            create_model_residuals_plot(y_test_sub, y_pred_sub),
            use_container_width=True
        )

st.markdown("---")

# Interactive Inference Sandbox
st.markdown("### 🧪 Real-Time Predictive Inference Sandbox")
st.caption("Input asset parameters to query the Scikit-Learn pipeline in real time for predicted loss ratio (%) and dollar loss ($M).")

with st.form("ml_inference_form"):
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("**1. Geographic & Climatic Context**")
        in_zone = st.selectbox("Climate Zone", ["Tropical", "Subtropical", "Temperate", "Arid", "Mediterranean", "Continental"], index=0)
        in_elev = st.number_input("Elevation (meters above sea level)", min_value=0.0, max_value=2500.0, value=12.0)
        in_coast = st.number_input("Distance to Coast (km)", min_value=0.5, max_value=800.0, value=4.0)
        in_sector = st.selectbox(
            "Industry Sector",
            [
                "Data Centers & IT Infrastructure",
                "Manufacturing & Heavy Industrial",
                "Agriculture & Food Supply",
                "Logistics, Ports & Warehousing",
                "Commercial Real Estate & Hospitality",
                "Renewable Energy & Utilities"
            ],
            index=1
        )
        
    with col_f2:
        st.markdown("**2. Physical Hazard Severity (0 - 100)**")
        in_flood = st.slider("Flood Hazard", 0.0, 100.0, 85.0)
        in_heat = st.slider("Extreme Heat Hazard", 0.0, 100.0, 78.0)
        in_drought = st.slider("Drought Hazard", 0.0, 100.0, 35.0)
        in_wildfire = st.slider("Wildfire Hazard", 0.0, 100.0, 20.0)
        in_rainfall = st.slider("Heavy Rainfall Hazard", 0.0, 100.0, 90.0)
        
    with col_f3:
        st.markdown("**3. Operational Scale & Defenses**")
        in_asset_val = st.number_input("Asset Value ($M USD)", min_value=10.0, max_value=2500.0, value=450.0, step=25.0)
        in_employees = st.number_input("Headcount", min_value=10, max_value=8000, value=850, step=50)
        in_bk_pwr = st.checkbox("Installed Backup Microgrid", value=True)
        in_fl_bar = st.checkbox("Installed Flood Barrier", value=True)
        in_wt_rec = st.checkbox("Closed-Loop Water System", value=False)
        
    submitted = st.form_submit_button("🚀 Run ML Predictive Inference", use_container_width=True)

if submitted:
    sample_payload = {
        "elevation_m": in_elev,
        "distance_to_coast_km": in_coast,
        "climate_zone": in_zone,
        "sector": in_sector,
        "flood_hazard": in_flood,
        "heat_hazard": in_heat,
        "drought_hazard": in_drought,
        "wildfire_hazard": in_wildfire,
        "rainfall_hazard": in_rainfall,
        "asset_value_m": in_asset_val,
        "employees": in_employees,
        "backup_power": 1 if in_bk_pwr else 0,
        "flood_barrier": 1 if in_fl_bar else 0,
        "water_recycling": 1 if in_wt_rec else 0
    }
    
    pred_res = predict_single_facility(pipeline, sample_payload)
    
    st.markdown(
        f"""
        <div class="metric-card" style="background: #EBF3EE; border-left: 6px solid #0F4C3A; margin-top: 16px;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #0F4C3A; margin-bottom: 6px;">🤖 ML Model Prediction Result</div>
            <div style="display: flex; gap: 32px; flex-wrap: wrap; margin-top: 8px;">
                <div>
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #718096; font-weight: 600;">Predicted Loss Ratio</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #E63946;">{pred_res['predicted_loss_ratio_pct']:.2f}%</div>
                </div>
                <div>
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #718096; font-weight: 600;">Estimated Annual Dollar Loss</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #0F4C3A;">${pred_res['predicted_dollar_loss_m']:.2f}M USD</div>
                </div>
                <div style="max-width: 400px; font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                    The Random Forest pipeline predicts an annual asset loss ratio of <b>{pred_res['predicted_loss_ratio_pct']:.2f}%</b> based on high flood & rainfall hazard mitigated by the installed flood wall and backup power.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Hyperparameter Control Panel (Model Retraining)
with st.expander("⚙️ Interactive Model Re-training & Hyperparameter Tuning", expanded=False):
    st.caption("Adjust Random Forest hyperparameters and trigger live training across 1,200 empirical climate benchmark events.")
    p_c1, p_c2, p_c3 = st.columns(3)
    with p_c1:
        hp_trees = st.slider("Number of Trees (n_estimators)", 40, 200, 120, step=20)
    with p_c2:
        hp_depth = st.slider("Max Tree Depth", 6, 20, 12)
    with p_c3:
        hp_test_size = st.slider("Test Split Size", 0.15, 0.35, 0.20, step=0.05)
        
    if st.button("🔄 Retrain Scikit-Learn Model Now"):
        with st.spinner("Retraining Random Forest Pipeline and calculating cross-validation scores..."):
            pipeline, metrics = get_trained_model(
                force_retrain=True,
                n_estimators=hp_trees,
                max_depth=hp_depth
            )
            st.success(f"Model successfully retrained! New Test R²: {metrics['r2_test']:.4f} | 3-Fold CV R²: {metrics['cv_r2_mean']:.4f}")
            st.rerun()
