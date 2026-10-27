"""
Scenario Explorer & Stress Testing Page — ClimateIQ.
Models IPCC AR6 Shared Socioeconomic Pathways (SSP1-2.6, SSP2-4.5, SSP5-8.5)
across 2030, 2040, and 2050 time horizons with macro stress-testing sliders.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.data_loader import load_facilities_data
from src.risk_scoring import score_facility_row, apply_scenario_projection
from src.visuals import create_scenario_projection_chart
from src.config import SCENARIOS, THEME_COLORS

st.set_page_config(page_title="Scenario Explorer | ClimateIQ", page_icon="🌐", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="IPCC Climate Scenario Explorer & Stress Testing",
    subtitle="Forward-looking risk modeling under IPCC AR6 Shared Socioeconomic Pathways (SSPs) through 2050 horizons.",
    icon="🌐"
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

sel_fac = st.selectbox("Select Enterprise Facility to Project", fac_names, index=default_idx)
st.session_state["selected_facility_name"] = sel_fac

row = df_facilities[df_facilities["facility_name"] == sel_fac].iloc[0]
base_res = score_facility_row(row)
base_score = base_res["overall_risk_score"]

# Overview of Scenarios Callout Cards
st.markdown("### 🌍 IPCC AR6 Shared Socioeconomic Pathways (SSPs)")
sc_c1, sc_c2, sc_c3 = st.columns(3)

with sc_c1:
    st.markdown(
        """
        <div class="metric-card" style="border-top: 4px solid #2A9D8F; min-height: 180px;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #2A9D8F;">SSP1-2.6: Sustainability</div>
            <div style="font-size: 0.8rem; color: #718096; margin-bottom: 6px;">Target: +1.5°C to +1.8°C by 2100</div>
            <div style="font-size: 0.85rem; color: #4A5568; line-height: 1.4;">
                Aggressive global decarbonization, strict climate transition policies, and rapid clean-tech adoption. Minimal hazard acceleration.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with sc_c2:
    st.markdown(
        """
        <div class="metric-card" style="border-top: 4px solid #E9C46A; min-height: 180px;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #D97706;">SSP2-4.5: Middle of the Road</div>
            <div style="font-size: 0.8rem; color: #718096; margin-bottom: 6px;">Target: +2.7°C by 2100</div>
            <div style="font-size: 0.85rem; color: #4A5568; line-height: 1.4;">
                Current global policy trajectory. Intermediate greenhouse emissions with moderate adaptation and uneven vulnerability increases.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with sc_c3:
    st.markdown(
        """
        <div class="metric-card" style="border-top: 4px solid #E63946; min-height: 180px;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #DC2626;">SSP5-8.5: Fossil Development</div>
            <div style="font-size: 0.8rem; color: #718096; margin-bottom: 6px;">Target: +4.4°C by 2100</div>
            <div style="font-size: 0.85rem; color: #4A5568; line-height: 1.4;">
                High reliance on fossil fuels, unmitigated greenhouse emissions, and extreme frequency of catastrophic multi-hazard events.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Trajectory Chart
st.markdown("### 📈 Facility Risk Trajectory (2024 — 2050)")
fig_traj = create_scenario_projection_chart(base_score)
st.plotly_chart(fig_traj, use_container_width=True)

# Comparative Scenario Matrix for selected facility
st.markdown(f"### 📊 Future Risk Ratings for **{row['facility_name']}** ({row['city']})")

years = ["2030", "2040", "2050"]
matrix_data = []

for sc_name, sc_info in SCENARIOS.items():
    row_dict = {"Scenario": sc_name.split(" ")[0]}
    for y in years:
        res = score_facility_row(row, scenario_name=sc_name, target_year=y)
        row_dict[f"{y} Score"] = f"{res['overall_risk_score']:.1f}/100"
        row_dict[f"{y} Tier"] = res["risk_tier"]
    matrix_data.append(row_dict)

st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

st.markdown("---")

# Portfolio Macro Stress Testing Sandbox
st.markdown("### 🌪️ Portfolio Macro Stress-Testing Simulator")
st.caption("Apply acute macro hazard shocks across all 25 corporate assets to simulate extreme climate tail-risk events.")

c_st1, c_st2, c_st3 = st.columns(3)
with c_st1:
    shock_flood = st.slider("Global Flood / Storm Surge Shock (+%)", 0, 50, 20, step=5)
with c_st2:
    shock_heat = st.slider("Extreme Heatwave Intensification (+%)", 0, 50, 25, step=5)
with c_st3:
    shock_rain = st.slider("Acute Storm Rainfall Surge (+%)", 0, 50, 15, step=5)

# Recalculate portfolio risk under shock
shocked_critical = 0
shocked_high = 0
shocked_avg_scores = []

for _, f_row in df_facilities.iterrows():
    base_res = score_facility_row(f_row)
    # Apply shock multipliers
    shock_score = base_res["overall_risk_score"] * (1.0 + (shock_flood*0.35 + shock_heat*0.35 + shock_rain*0.30)/100.0)
    shock_score = min(100.0, shock_score)
    shocked_avg_scores.append(shock_score)
    if shock_score > 75:
        shocked_critical += 1
    elif shock_score > 50:
        shocked_high += 1

m1, m2, m3 = st.columns(3)
with m1:
    render_metric_card("Stressed Mean Risk", f"{sum(shocked_avg_scores)/len(shocked_avg_scores):.1f} / 100", f"+{(sum(shocked_avg_scores)/len(shocked_avg_scores)) - base_score:.1f} pts jump", delta_color="#E63946")
with m2:
    render_metric_card("Critical Assets Post-Shock", f"{shocked_critical} / 25", f"{(shocked_critical/25)*100:.0f}% of portfolio", delta_color="#E63946")
with m3:
    render_metric_card("Total High & Critical Exposure", f"{shocked_critical + shocked_high} / 25", "Assets requiring immediate capital retrofits", delta_color="#F4A261")
