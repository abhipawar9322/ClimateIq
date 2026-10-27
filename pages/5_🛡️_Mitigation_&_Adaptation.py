"""
Mitigation & Adaptation Planner Page — ClimateIQ.
Actionable climate resilience roadmaps, CapEx/OpEx ROI modeling,
and TCFD / CSRD disclosure report export (PDF, Markdown, CSV).
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
from src.risk_scoring import score_facility_row, calculate_overall_climate_risk
from src.financial_model import calculate_business_impacts, calculate_adaptation_roi
from src.report_generator import (
    generate_executive_markdown_report,
    generate_executive_pdf_report
)
from src.config import THEME_COLORS

st.set_page_config(page_title="Mitigation & Adaptation | ClimateIQ", page_icon="🛡️", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Mitigation Strategies & Adaptation Planning",
    subtitle="Actionable engineering interventions, CapEx resilience ROI modeling, and board-ready TCFD/CSRD disclosure reports.",
    icon="🛡️"
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

sel_fac = st.selectbox("Select Facility for Adaptation Planning", fac_names, index=default_idx)
st.session_state["selected_facility_name"] = sel_fac

row = df_facilities[df_facilities["facility_name"] == sel_fac].iloc[0]

# Calculate baseline metrics
hazards_dict = {
    "Flood Risk": float(row["flood_hazard"]),
    "Extreme Heat Risk": float(row["heat_hazard"]),
    "Drought Risk": float(row["drought_hazard"]),
    "Wildfire Risk": float(row["wildfire_hazard"]),
    "Heavy Rainfall Risk": float(row["rainfall_hazard"]),
}
sector = str(row["sector"])
asset_val = float(row["asset_value_m"])
revenue = float(row["annual_revenue_m"])
employees = int(row["employees"])
bk_pwr = bool(row["backup_power"])
fl_bar = bool(row["flood_barrier"])
wt_rec = bool(row["water_recycling"])

risk_score, tier, color = calculate_overall_climate_risk(
    hazards_dict, sector, bk_pwr, fl_bar, wt_rec
)
risk_summary = score_facility_row(row)
impacts = calculate_business_impacts(
    asset_val, revenue, employees, risk_score, sector, hazards_dict, bk_pwr, fl_bar, wt_rec
)

# Dynamic tailored action items based on top hazards
actions = []
if hazards_dict["Flood Risk"] > 50 or hazards_dict["Heavy Rainfall Risk"] > 50:
    actions.append({
        "action": "Deploy Modular Deployable Flood Walls & Sump Pumping Arrays",
        "category": "Structural Engineering",
        "capex": "$3.5M - $6.0M",
        "reduction": "60% - 80% flood damage reduction",
        "description": "Construct demountable flood barrier gates at ingress points, elevate critical electrical switchgear by 1.8m, and install redundant automated sump pumps."
    })
if hazards_dict["Extreme Heat Risk"] > 60:
    actions.append({
        "action": "Cool Roof Retrofits & Hybrid Adiabatic Chiller Upgrades",
        "category": "Thermal Resilience",
        "capex": "$1.2M - $2.5M",
        "reduction": "30% cooling load reduction; 85% worker heat stress reduction",
        "description": "Apply high-albedo solar-reflective coating to rooftops and replace aging HVAC with closed-loop adiabatic chillers to withstand >45°C ambient heat waves."
    })
if hazards_dict["Drought Risk"] > 50:
    actions.append({
        "action": "Closed-Loop Wastewater Recycling & Rainwater Harvesting",
        "category": "Operational Resource Conservation",
        "capex": "$2.0M - $4.0M",
        "reduction": "50% freshwater dependency reduction",
        "description": "Implement membrane bioreactor (MBR) industrial water recycling to insulate cooling towers and manufacturing processes from municipal water rationing."
    })
if hazards_dict["Wildfire Risk"] > 50:
    actions.append({
        "action": "Defensible Perimeter Zone & Industrial HEPA Air Intakes",
        "category": "Perimeter & Air Quality Defense",
        "capex": "$0.8M - $1.8M",
        "reduction": "75% smoke particulate damage reduction",
        "description": "Establish a 30-meter defensible fuel-free perimeter around assets and upgrade ventilation to MERV 16 / HEPA filters to protect workforce and sensitive machinery."
    })
# Always include parametric insurance & ESG disclosure
actions.append({
    "action": "Parametric Weather Index Insurance & TCFD Climate Risk Transfer",
    "category": "Financial Risk Transfer",
    "capex": "Low CapEx / $0.4M OpEx",
    "reduction": "100% rapid liquidity payout within 7 days of verified storm trigger",
    "description": "Contract parametric insurance policies pegged directly to satellite rainfall and heat index thresholds to eliminate protracted loss adjustment delays."
})

# Display Action Cards
st.markdown("### 📋 Prioritized Adaptation Interventions")
for i, act in enumerate(actions, 1):
    with st.container():
        st.markdown(
            f"""
            <div class="metric-card" style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F4C3A;">{i}. {act['action']}</div>
                    <span class="risk-badge badge-low">{act['category']}</span>
                </div>
                <div style="margin: 6px 0; font-size: 0.88rem; color: #4A5568;">{act['description']}</div>
                <div style="display: flex; gap: 20px; font-size: 0.82rem; color: #718096; margin-top: 8px;">
                    <div><b>Est. CapEx:</b> {act['capex']}</div>
                    <div><b>Target Efficacy:</b> {act['reduction']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# Adaptation ROI & Cost-Benefit Modeling
st.markdown("### 💰 CapEx Resilience Investment & ROI Calculator")
st.caption("Model the return on investment (ROI) and Net Present Value (NPV) of physical resilience retrofits over a 10-year capital horizon.")

roi_c1, roi_c2, roi_c3, roi_c4 = st.columns(4)

with roi_c1:
    in_capex = st.number_input("Resilience CapEx ($M USD)", min_value=0.5, max_value=50.0, value=6.5, step=0.5)
with roi_c2:
    in_opex = st.number_input("Annual Maintenance OpEx ($M)", min_value=0.05, max_value=5.0, value=0.25, step=0.05)
with roi_c3:
    in_reduction = st.slider("Expected Loss Reduction (%)", 20.0, 90.0, 65.0, step=5.0)
with roi_c4:
    in_discount = st.slider("Discount Rate (%)", 3.0, 12.0, 6.0, step=0.5)

roi_res = calculate_adaptation_roi(
    current_annual_var_m=impacts["total_climate_var_m"],
    capex_cost_m=in_capex,
    opex_annual_m=in_opex,
    loss_reduction_pct=in_reduction,
    time_horizon_years=10,
    discount_rate=in_discount / 100.0
)

# ROI Metric Cards
r1, r2, r3, r4 = st.columns(4)
with r1:
    render_metric_card("Annual Avoided Loss", f"${roi_res['annual_avoided_loss_m']:.2f} M", f"{in_reduction:.0f}% risk reduction")
with r2:
    render_metric_card("10-Year Net Present Value (NPV)", f"${roi_res['npv_m']:.2f} M", "Discounted Cash Flow", delta_color="#2A9D8F" if roi_res['npv_m'] > 0 else "#E63946")
with r3:
    render_metric_card("Capital Payback Period", f"{roi_res['payback_years']:.1f} Years", "Time to recover CapEx")
with r4:
    render_metric_card("10-Year Resilience ROI", f"{roi_res['roi_10yr_pct']:.0f}%", "Net financial yield", delta_color="#2A9D8F")

st.markdown("---")

# Executive Briefing & Disclosure Downloads
st.markdown("### 📥 Download Executive Climate Risk & Disclosure Reports")
st.caption("Generate official PDF briefings, Markdown board memos, and audit-ready CSV exports aligned with TCFD Strategy Recommendation b.")

d_col1, d_col2, d_col3 = st.columns(3)

# 1. PDF Report
with d_col1:
    pdf_bytes = generate_executive_pdf_report(
        facility_data=row.to_dict(),
        hazards_data=hazards_dict,
        risk_summary=risk_summary,
        financial_data=impacts
    )
    st.download_button(
        label="📄 Download Official PDF Report",
        data=pdf_bytes,
        file_name=f"ClimateIQ_Risk_Report_{row['city']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# 2. Markdown Report
with d_col2:
    md_content = generate_executive_markdown_report(
        facility_data=row.to_dict(),
        hazards_data=hazards_dict,
        risk_summary=risk_summary,
        financial_data=impacts,
        mitigation_actions=actions
    )
    st.download_button(
        label="📝 Download Markdown Brief",
        data=md_content,
        file_name=f"ClimateIQ_Executive_Brief_{row['city']}.md",
        mime="text/markdown",
        use_container_width=True
    )

# 3. CSV Dataset Export
with d_col3:
    csv_bytes = df_facilities.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download Portfolio CSV Audit",
        data=csv_bytes,
        file_name="ClimateIQ_Portfolio_Audit.csv",
        mime="text/csv",
        use_container_width=True
    )
