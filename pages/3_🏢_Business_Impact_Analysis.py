"""
Business Impact Analysis Page — ClimateIQ.
Translates climate hazard scores into financial and operational corporate loss metrics:
Expected Annual Loss (EAL), Business Interruption Days, Revenue at Risk, Worker Heat Drag, and Insurance Loading.
"""

import streamlit as st
import pandas as pd
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.data_loader import load_facilities_data
from src.risk_scoring import calculate_overall_climate_risk
from src.financial_model import calculate_business_impacts
from src.visuals import create_financial_loss_waterfall
from src.config import SECTOR_VULNERABILITIES

st.set_page_config(page_title="Business Impact Analysis | ClimateIQ", page_icon="🏢", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Business & Financial Impact Analysis",
    subtitle="Quantification of Expected Annual Loss (EAL), business interruption downtime, revenue-at-risk, and insurance loading.",
    icon="🏢"
)

# Load data
df_facilities = load_facilities_data()
fac_names = df_facilities["facility_name"].tolist()

default_idx = 0
if "selected_facility_name" in st.session_state:
    try:
        default_idx = fac_names.index(st.session_state["selected_facility_name"])
    except ValueError:
        default_idx = 0

sel_fac = st.selectbox("Select Enterprise Facility to Model", fac_names, index=default_idx)
st.session_state["selected_facility_name"] = sel_fac

row = df_facilities[df_facilities["facility_name"] == sel_fac].iloc[0]

# Baseline Facility Info
hazards_dict = {
    "Flood Risk": float(row["flood_hazard"]),
    "Extreme Heat Risk": float(row["heat_hazard"]),
    "Drought Risk": float(row["drought_hazard"]),
    "Wildfire Risk": float(row["wildfire_hazard"]),
    "Heavy Rainfall Risk": float(row["rainfall_hazard"]),
}
sector = str(row["sector"])

st.markdown("### 🎛️ Operational & Resilience Sensitivity Modeling")
st.caption("Adjust facility operational variables or toggle engineering defenses to simulate impact on corporate financial loss.")

col_sim1, col_sim2, col_sim3, col_sim4 = st.columns(4)

with col_sim1:
    sim_asset_val = st.number_input(
        "Asset Replacement Value ($M)",
        min_value=10.0,
        max_value=2500.0,
        value=float(row["asset_value_m"]),
        step=25.0
    )
with col_sim2:
    sim_rev = st.number_input(
        "Annual Operating Revenue ($M)",
        min_value=5.0,
        max_value=3000.0,
        value=float(row["annual_revenue_m"]),
        step=25.0
    )
with col_sim3:
    sim_employees = st.number_input(
        "Workforce Headcount",
        min_value=20,
        max_value=10000,
        value=int(row["employees"]),
        step=50
    )
with col_sim4:
    st.markdown("**Installed Defenses**")
    sim_bk_pwr = st.checkbox("Backup Microgrid", value=bool(row["backup_power"]))
    sim_fl_bar = st.checkbox("Physical Flood Barrier", value=bool(row["flood_barrier"]))
    sim_wt_rec = st.checkbox("Closed-Loop Water", value=bool(row["water_recycling"]))

# Calculate risk and financial impact
risk_score, tier, color = calculate_overall_climate_risk(
    hazards_dict, sector, sim_bk_pwr, sim_fl_bar, sim_wt_rec
)

impacts = calculate_business_impacts(
    asset_value_m=sim_asset_val,
    annual_revenue_m=sim_rev,
    employees=sim_employees,
    risk_score=risk_score,
    sector=sector,
    hazards_dict=hazards_dict,
    has_backup_power=sim_bk_pwr,
    has_flood_barrier=sim_fl_bar,
    has_water_recycling=sim_wt_rec
)

# Financial KPI Metrics Row
st.markdown("### 💵 Modeled Annual Financial Exposure")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    render_metric_card(
        "Total Climate VaR (Annual)",
        f"${impacts['total_climate_var_m']:.2f} M",
        f"{(impacts['total_climate_var_m']/sim_asset_val)*100:.2f}% of asset value",
        delta_color="#E63946"
    )
with kpi2:
    render_metric_card(
        "Expected Physical Damage",
        f"${impacts['expected_physical_loss_m']:.2f} M",
        f"Damage Ratio: {impacts['damage_ratio_pct']:.2f}%"
    )
with kpi3:
    render_metric_card(
        "Business Interruption Loss",
        f"${impacts['revenue_at_risk_m']:.2f} M",
        f"~{impacts['downtime_days']:.1f} Operating Days Down",
        delta_color="#F4A261"
    )
with kpi4:
    render_metric_card(
        "Workforce Heat / Smoke Drag",
        f"${impacts['workforce_cost_m']:.2f} M",
        f"-{impacts['worker_productivity_loss_pct']:.1f}% labor efficiency"
    )

# Waterfall Chart
st.markdown("### 🌊 Climate Value-at-Risk (VaR) Decomposition")
st.plotly_chart(create_financial_loss_waterfall(impacts), use_container_width=True)

# Secondary Impact Table & Insurance Loading
st.markdown("---")
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown("### 🛡️ Projected Commercial Insurance Impact")
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F4C3A; margin-bottom: 8px;">Property & Casualty Underwriting Risk</div>
            <div style="font-size: 0.9rem; color: #4A5568; line-height: 1.6;">
                Due to the facility's <b>{tier.upper()} RISK</b> classification (Score: {risk_score:.1f}/100), insurers are imposing severe underwriting surcharges.
            </div>
            <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #718096;">Baseline Premium:</span>
                <span style="font-weight: 600;">${impacts['base_insurance_premium_m']:.2f}M / yr</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #718096;">Climate Surcharge Loading:</span>
                <span style="font-weight: 700; color: #E63946;">+{impacts['insurance_surge_pct']:.1f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #E2E8F0;">
                <span style="font-weight: 700; color: #1A202C;">Projected Renewal Premium:</span>
                <span style="font-weight: 800; font-size: 1.15rem; color: #0F4C3A;">${impacts['projected_insurance_m']:.2f}M / yr</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c_right:
    st.markdown("### 🏭 Industry Sector Downtime Exposure Benchmarks")
    sector_df = pd.DataFrame([
        {"Sector": k, "Base Outage Cost ($/Day)": f"${v['base_downtime_cost_per_day']:,}", "Labor Heat Sensitivity": f"{v['worker_density']*100:.0f}%"}
        for k, v in SECTOR_VULNERABILITIES.items()
    ])
    st.dataframe(sector_df, use_container_width=True, hide_index=True)
