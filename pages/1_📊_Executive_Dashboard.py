"""
Executive Dashboard Page — ClimateIQ.
High-level enterprise portfolio monitoring, geospatial risk mapping, and risk distribution metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.data_loader import load_facilities_data
from src.risk_scoring import score_facility_row
from src.visuals import create_global_risk_map
from src.config import THEME_COLORS, RISK_TIERS

st.set_page_config(page_title="Executive Dashboard | ClimateIQ", page_icon="📊", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Executive Portfolio Dashboard",
    subtitle="Global enterprise asset distribution, geospatial hazard exposure, and risk tier categorization.",
    icon="📊"
)

# Load data and score
df_facilities = load_facilities_data()
scenario_name = st.session_state.get("selected_scenario", "Baseline (Current 2024)")
target_year = st.session_state.get("selected_year", "2040")
scen_key = None if "Baseline" in scenario_name else scenario_name

scored_rows = [score_facility_row(row, scenario_name=scen_key, target_year=target_year) for _, row in df_facilities.iterrows()]
df_scored = df_facilities.copy()
df_scored["overall_risk_score"] = [r["overall_risk_score"] for r in scored_rows]
df_scored["risk_tier"] = [r["risk_tier"] for r in scored_rows]
df_scored["composite_hazard"] = [r["composite_hazard"] for r in scored_rows]
df_scored["vulnerability_factor"] = [r["vulnerability_factor"] for r in scored_rows]

# Interactive Filter Bar
with st.expander("🔍 Filter Asset Portfolio", expanded=False):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        all_sectors = sorted(df_scored["sector"].unique().tolist())
        sel_sectors = st.multiselect("Sector", all_sectors, default=all_sectors)
    with f_col2:
        all_tiers = list(RISK_TIERS.keys())
        sel_tiers = st.multiselect("Risk Tier", all_tiers, default=all_tiers)
    with f_col3:
        all_countries = sorted(df_scored["country"].unique().tolist())
        sel_countries = st.multiselect("Country", all_countries, default=all_countries)

# Apply filters
df_filtered = df_scored[
    (df_scored["sector"].isin(sel_sectors)) &
    (df_scored["risk_tier"].isin(sel_tiers)) &
    (df_scored["country"].isin(sel_countries))
]

if df_filtered.empty:
    st.warning("No facilities match the selected filters. Resetting to full portfolio.")
    df_filtered = df_scored

# Top KPI row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    tot_val = df_filtered["asset_value_m"].sum()
    render_metric_card("Filtered Asset Value", f"${tot_val:,.1f} M", f"{len(df_filtered)} Facilities")
with kpi2:
    mean_score = df_filtered["overall_risk_score"].mean()
    render_metric_card("Portfolio Mean Risk", f"{mean_score:.1f} / 100", f"Range: {df_filtered['overall_risk_score'].min():.1f} - {df_filtered['overall_risk_score'].max():.1f}")
with kpi3:
    crit_count = len(df_filtered[df_filtered["risk_tier"] == "Critical"])
    render_metric_card("Critical Assets", f"{crit_count}", f"Immediate action needed", delta_color="#E63946")
with kpi4:
    high_count = len(df_filtered[df_filtered["risk_tier"] == "High"])
    render_metric_card("High Risk Assets", f"{high_count}", f"Vulnerability > 50", delta_color="#F4A261")

# Global Geospatial Map
st.markdown("### 🗺️ Enterprise Asset Vulnerability Map")
st.caption("Circle size represents Asset Replacement Value ($M USD). Color indicates composite climate risk tier.")
fig_map = create_global_risk_map(df_filtered)
st.plotly_chart(fig_map, use_container_width=True)

# Risk Distribution Charts
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown("### 🍩 Portfolio Risk Tier Distribution")
    tier_counts = df_filtered["risk_tier"].value_counts().reset_index()
    tier_counts.columns = ["Tier", "Count"]
    
    color_map = {tier: data["color"] for tier, data in RISK_TIERS.items()}
    
    fig_donut = px.pie(
        tier_counts,
        names="Tier",
        values="Count",
        hole=0.55,
        color="Tier",
        color_discrete_map=color_map,
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with c_right:
    st.markdown("### 🏭 Mean Risk Score by Sector")
    sector_means = df_filtered.groupby("sector")["overall_risk_score"].mean().reset_index().sort_values(by="overall_risk_score", ascending=True)
    
    fig_bar = px.bar(
        sector_means,
        x="overall_risk_score",
        y="sector",
        orientation="h",
        labels={"overall_risk_score": "Average Risk (0-100)", "sector": ""},
        color="overall_risk_score",
        color_continuous_scale=["#2A9D8F", "#E9C46A", "#F4A261", "#E63946"],
        range_color=[20, 90]
    )
    fig_bar.update_layout(
        margin=dict(l=10, r=20, t=20, b=20),
        height=320,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FAFCFB"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Top 5 Vulnerable Facilities Alert Table
st.markdown("### ⚠️ Top 5 Highest Risk Facilities")
top_5 = df_filtered.sort_values(by="overall_risk_score", ascending=False).head(5)

for _, fac in top_5.iterrows():
    with st.container():
        st.markdown(
            f"""
            <div class="metric-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 20px;">
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F4C3A;">{fac['facility_name']}</div>
                    <div style="font-size: 0.85rem; color: #4A5568;">{fac['city']}, {fac['country']} | <b>{fac['sector']}</b></div>
                </div>
                <div style="display: flex; align-items: center; gap: 24px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #718096; text-transform: uppercase;">Asset Value</div>
                        <div style="font-weight: 700; font-size: 1.1rem; color: #1A202C;">${fac['asset_value_m']:.1f}M</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #718096; text-transform: uppercase;">Risk Score</div>
                        <div style="font-weight: 800; font-size: 1.25rem; color: {RISK_TIERS.get(fac['risk_tier'], {}).get('color', '#E63946')};">{fac['overall_risk_score']:.1f}/100</div>
                    </div>
                    <div>
                        <span class="risk-badge badge-{fac['risk_tier'].lower()}">{fac['risk_tier']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
