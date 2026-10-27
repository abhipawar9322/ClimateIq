"""
ClimateIQ — Climate Risk Intelligence Platform.
Main Entrypoint and Platform Overview.
"""

import streamlit as st
import pandas as pd
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.data_loader import load_facilities_data, load_locations_data
from src.risk_scoring import score_facility_row
from src.config import THEME_COLORS

# Configure Streamlit page
st.set_page_config(
    page_title="ClimateIQ | Climate Risk Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()
render_sidebar_brand()

# Sidebar global scenario and persistence
with st.sidebar:
    st.markdown("### ⚙️ Global Analysis Settings")
    selected_scenario = st.selectbox(
        "IPCC Climate Pathway",
        [
            "Baseline (Current 2024)",
            "SSP1-2.6 (Paris Aligned - Low Warming)",
            "SSP2-4.5 (Middle of the Road - Current Policy)",
            "SSP5-8.5 (Fossil-Fueled Development - High Risk)"
        ],
        index=0,
        help="Select IPCC AR6 Shared Socioeconomic Pathway to project hazards."
    )
    st.session_state["selected_scenario"] = selected_scenario
    
    selected_year = st.selectbox(
        "Projection Horizon",
        ["2030", "2040", "2050"],
        index=1,
        help="Target year for future climate risk modeling."
    )
    st.session_state["selected_year"] = selected_year
    
    st.markdown("---")
    st.info("💡 **Tip**: Navigate through the pages in the left sidebar to access deep-dive hazard assessments, business impact models, and AI predictions.")

# Header
render_page_header(
    title="ClimateIQ: Climate Risk Intelligence Platform",
    subtitle="Enterprise physical climate risk analytics, business impact quantification, and AI-driven adaptation modeling.",
    icon="🌿"
)

# Load data
df_facilities = load_facilities_data()

# Compute scores for all facilities
scenario_key = None if "Baseline" in selected_scenario else selected_scenario
scored_rows = []
for _, row in df_facilities.iterrows():
    res = score_facility_row(row, scenario_name=scenario_key, target_year=selected_year)
    scored_rows.append(res)
    
df_scored = df_facilities.copy()
df_scored["overall_risk_score"] = [r["overall_risk_score"] for r in scored_rows]
df_scored["risk_tier"] = [r["risk_tier"] for r in scored_rows]
df_scored["composite_hazard"] = [r["composite_hazard"] for r in scored_rows]
df_scored["vulnerability_factor"] = [r["vulnerability_factor"] for r in scored_rows]

# Top KPI metrics
col1, col2, col3, col4 = st.columns(4)

total_asset_val_b = df_scored["asset_value_m"].sum() / 1000.0
avg_risk = df_scored["overall_risk_score"].mean()
high_critical_count = len(df_scored[df_scored["risk_tier"].isin(["High", "Critical"])])
total_facilities = len(df_scored)

with col1:
    render_metric_card("Total Assessed Portfolio", f"${total_asset_val_b:.2f} B", "25 Global Facilities")
with col2:
    render_metric_card("Average Climate Risk", f"{avg_risk:.1f} / 100", f"{selected_scenario.split(' ')[0]}")
with col3:
    render_metric_card("Critical & High Risk Assets", f"{high_critical_count} / {total_facilities}", f"{(high_critical_count/total_facilities)*100:.0f}% of portfolio", delta_color="#E63946")
with col4:
    render_metric_card("Framework Compliance", "IPCC AR6", "TCFD & CSRD Aligned", delta_color="#2A9D8F")

st.markdown("---")

# Quick Navigation & Feature Highlights
st.markdown("### 🧭 Platform Capabilities & Modules")

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">📊</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">1. Executive Dashboard</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                Global asset portfolio overview, geospatial risk heatmaps, risk tier distribution, and high-exposure facility screening.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-low">Geospatial Mapping</span>
                <span class="risk-badge badge-moderate">Portfolio KPIs</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m_col2:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">🌪️</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">2. Climate Risk Assessment</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                Deep-dive hazard breakdown for Flood, Extreme Heat, Drought, Wildfire, and Heavy Rainfall with multi-hazard spider charts.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-low">5 Hazard Indices</span>
                <span class="risk-badge badge-high">Transparent Math</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m_col3:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">🏢</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">3. Business Impact Analysis</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                Financial quantification of Expected Annual Loss (EAL), downtime days, workforce heat stress drag, and insurance surges.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-moderate">Climate VaR</span>
                <span class="risk-badge badge-critical">Downtime Loss</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

m_col4, m_col5, m_col6 = st.columns(3)

with m_col4:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">🤖</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">4. Predictive ML Risk Engine</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                Real Scikit-Learn Random Forest Regressor predicting asset loss ratios with cross-validated metrics, SHAP/feature rankings, and live inference.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-low">Scikit-Learn</span>
                <span class="risk-badge badge-moderate">R² = 0.84+</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m_col5:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">🛡️</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">5. Mitigation & Adaptation</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                Prioritized engineering interventions, 10-year CapEx ROI & NPV modeling, and downloadable board-ready PDF/Markdown disclosure briefs.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-low">ROI & NPV</span>
                <span class="risk-badge badge-moderate">PDF Export</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m_col6:
    st.markdown(
        """
        <div class="metric-card" style="min-height: 220px;">
            <div style="font-size: 1.6rem; margin-bottom: 8px;">🌐</div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #0F4C3A; margin-bottom: 6px;">6. Scenarios & Live API</div>
            <div style="font-size: 0.88rem; color: #4A5568; line-height: 1.5;">
                IPCC AR6 multi-scenario stress-testing (SSP1-2.6 to SSP5-8.5 through 2050) plus real-time live meteorological telemetry via Open-Meteo.
            </div>
            <div style="margin-top: 14px;">
                <span class="risk-badge badge-low">Live Weather</span>
                <span class="risk-badge badge-high">2050 Horizon</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Executive Portfolio Highlight Table
st.markdown("### 🏢 Enterprise Facility Portfolio Screening")
st.dataframe(
    df_scored[[
        "facility_id", "facility_name", "sector", "city", "country",
        "asset_value_m", "overall_risk_score", "risk_tier"
    ]].sort_values(by="overall_risk_score", ascending=False).reset_index(drop=True),
    use_container_width=True,
    column_config={
        "facility_id": "ID",
        "facility_name": "Facility Name",
        "sector": "Industry Sector",
        "city": "City",
        "country": "Country",
        "asset_value_m": st.column_config.NumberColumn("Asset Value ($M)", format="$%.1fM"),
        "overall_risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%.1f"),
        "risk_tier": "Risk Tier"
    }
)
