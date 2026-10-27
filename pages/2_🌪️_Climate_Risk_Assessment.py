"""
Climate Risk Assessment Page — ClimateIQ.
Deep-dive multi-hazard risk engine analyzing Flood, Extreme Heat, Drought, Wildfire, and Heavy Rainfall.
Provides transparent mathematical scoring, radar benchmarking, and historical hazard logs.
"""

import streamlit as st
import pandas as pd
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.data_loader import load_facilities_data, load_historical_hazards
from src.risk_scoring import (
    score_facility_row,
    compute_composite_hazard_score,
    calculate_overall_climate_risk,
    compute_vulnerability_index
)
from src.visuals import (
    create_risk_gauge,
    create_multi_hazard_radar,
    create_hazard_breakdown_bars
)
from src.config import HAZARDS, HAZARD_ICONS, HAZARD_DESCRIPTIONS, RISK_TIERS

st.set_page_config(page_title="Climate Risk Assessment | ClimateIQ", page_icon="🌪️", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Climate Hazard & Risk Assessment",
    subtitle="Granular evaluation of physical climate hazards, vulnerability modulation, and scientific risk attribution.",
    icon="🌪️"
)

# Load data
df_facilities = load_facilities_data()
df_hist = load_historical_hazards()

# Mode selection: Existing Facility or Custom Location
mode = st.radio(
    "Assessment Mode",
    ["Select from Corporate Portfolio", "Custom Location & Hazard Sandbox"],
    horizontal=True
)

if mode == "Select from Corporate Portfolio":
    fac_names = df_facilities["facility_name"].tolist()
    # Check if a facility was previously chosen in session
    default_idx = 0
    if "selected_facility_name" in st.session_state:
        try:
            default_idx = fac_names.index(st.session_state["selected_facility_name"])
        except ValueError:
            default_idx = 0
            
    sel_fac_name = st.selectbox("Choose Facility to Analyze", fac_names, index=default_idx)
    st.session_state["selected_facility_name"] = sel_fac_name
    
    fac_row = df_facilities[df_facilities["facility_name"] == sel_fac_name].iloc[0]
    
    hazards_dict = {
        "Flood Risk": float(fac_row["flood_hazard"]),
        "Extreme Heat Risk": float(fac_row["heat_hazard"]),
        "Drought Risk": float(fac_row["drought_hazard"]),
        "Wildfire Risk": float(fac_row["wildfire_hazard"]),
        "Heavy Rainfall Risk": float(fac_row["rainfall_hazard"]),
    }
    sector = str(fac_row["sector"])
    city = str(fac_row["city"])
    country = str(fac_row["country"])
    asset_val = float(fac_row["asset_value_m"])
    bk_pwr = bool(fac_row["backup_power"])
    fl_bar = bool(fac_row["flood_barrier"])
    wt_rec = bool(fac_row["water_recycling"])
    
else:
    st.markdown("#### 🛠️ Custom Location Parameters")
    c1, c2, c3 = st.columns(3)
    with c1:
        city = st.text_input("Location / City Name", "Coastal Industrial Zone")
        country = st.text_input("Country", "Global")
    with c2:
        sector = st.selectbox(
            "Industry Sector",
            [
                "Manufacturing & Heavy Industrial",
                "Data Centers & IT Infrastructure",
                "Agriculture & Food Supply",
                "Logistics, Ports & Warehousing",
                "Commercial Real Estate & Hospitality",
                "Renewable Energy & Utilities"
            ]
        )
        asset_val = st.number_input("Asset Value ($M USD)", min_value=1.0, max_value=2000.0, value=350.0)
    with c3:
        st.markdown("**Installed Defenses**")
        bk_pwr = st.checkbox("Backup Microgrid / Power", True)
        fl_bar = st.checkbox("Flood Barriers / Sea Walls", False)
        wt_rec = st.checkbox("Water Recycling System", False)
        
    st.markdown("#### 🎚️ Physical Hazard Sliders (0 - 100)")
    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns(5)
    with h_col1:
        fl_val = st.slider("Flood Risk", 0.0, 100.0, 75.0)
    with h_col2:
        ht_val = st.slider("Extreme Heat", 0.0, 100.0, 80.0)
    with h_col3:
        dr_val = st.slider("Drought Risk", 0.0, 100.0, 45.0)
    with h_col4:
        wf_val = st.slider("Wildfire Risk", 0.0, 100.0, 30.0)
    with h_col5:
        rf_val = st.slider("Heavy Rainfall", 0.0, 100.0, 70.0)
        
    hazards_dict = {
        "Flood Risk": fl_val,
        "Extreme Heat Risk": ht_val,
        "Drought Risk": dr_val,
        "Wildfire Risk": wf_val,
        "Heavy Rainfall Risk": rf_val,
    }

# Compute scores
comp_hazard = compute_composite_hazard_score(hazards_dict)
vuln_index = compute_vulnerability_index(sector, hazards_dict, bk_pwr, fl_bar, wt_rec)
risk_score, tier_name, tier_color = calculate_overall_climate_risk(
    hazards_dict, sector, bk_pwr, fl_bar, wt_rec
)

# Header Summary Card
st.markdown(
    f"""
    <div class="metric-card" style="border-left: 6px solid {tier_color}; margin-top: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 1.3rem; font-weight: 800; color: #0F4C3A;">{city}, {country}</span>
                <span style="margin-left: 10px; font-size: 0.9rem; color: #718096;">Sector: <b>{sector}</b></span>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 1.1rem; font-weight: 700; color: {tier_color};">Risk Score: {risk_score:.1f}/100</span>
                <span class="risk-badge badge-{tier_name.lower()}">{tier_name} Risk</span>
            </div>
        </div>
        <div style="margin-top: 8px; font-size: 0.88rem; color: #4A5568;">
            {RISK_TIERS[tier_name]['description']}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Visuals Row
col_gauge, col_radar = st.columns([1, 1.2])

with col_gauge:
    st.plotly_chart(create_risk_gauge(risk_score, title=f"{city} Composite Risk"), use_container_width=True)

with col_radar:
    # Portfolio average benchmark
    benchmark_hazards = {
        "Flood Risk": 65.0,
        "Extreme Heat Risk": 72.0,
        "Drought Risk": 48.0,
        "Wildfire Risk": 38.0,
        "Heavy Rainfall Risk": 68.0
    }
    st.plotly_chart(create_multi_hazard_radar(hazards_dict, benchmark_hazards), use_container_width=True)

# Hazard Bars
st.markdown("### 📊 Granular Hazard Spectrum Breakdown")
st.plotly_chart(create_hazard_breakdown_bars(hazards_dict), use_container_width=True)

# Transparent Methodology Formula Expander
with st.expander("🔬 Mathematical Scoring Methodology & Weights (Transparent Algorithm)", expanded=False):
    st.markdown(
        r"""
        #### IPCC AR6 Risk Equation
        $$\text{Climate Risk} = \text{Hazard} \times \text{Exposure} \times \text{Vulnerability}$$
        
        Where:
        1. **Composite Hazard ($H$)**: Weighted combination of physical hazard intensities:
           $$H = \sum_{i} w_i \cdot H_i = 0.25 \times \text{Flood} + 0.20 \times \text{Heat} + 0.18 \times \text{Drought} + 0.17 \times \text{Wildfire} + 0.20 \times \text{Rainfall}$$
        2. **Sector Sensitivity ($S$)**: Empirical coefficient between 0.30 and 1.0 reflecting industry-specific operational exposure to active hazards.
        3. **Adaptive Capacity ($A$)**: Defense discounts:
           - Backup Power: $+35\%$
           - Flood Barriers: $+35\%$
           - Water Recycling: $+30\%$
           $$\text{Adaptive Capacity} = \sum \text{Defenses}$$
        4. **Net Vulnerability Factor ($V$)**:
           $$V = S \times (1.0 - 0.70 \times A)$$
        5. **Overall Risk Score ($R$)**:
           $$R = H \times (0.35 + 0.65 \times V) \in [0, 100]$$
        """
    )
    
    eq_c1, eq_c2, eq_c3 = st.columns(3)
    eq_c1.metric("Composite Hazard (H)", f"{comp_hazard:.1f} / 100")
    eq_c2.metric("Vulnerability Factor (V)", f"{vuln_index:.2f}")
    eq_c3.metric("Computed Composite Risk", f"{risk_score:.1f} / 100")

st.markdown("---")

# Deep-dive tabs for the 5 hazards
st.markdown("### 🔍 Hazard Deep-Dive & Physical Drivers")
t1, t2, t3, t4, t5 = st.tabs([
    f"{HAZARD_ICONS['Flood Risk']} Flood",
    f"{HAZARD_ICONS['Extreme Heat Risk']} Extreme Heat",
    f"{HAZARD_ICONS['Drought Risk']} Drought",
    f"{HAZARD_ICONS['Wildfire Risk']} Wildfire",
    f"{HAZARD_ICONS['Heavy Rainfall Risk']} Heavy Rainfall"
])

with t1:
    st.markdown(f"**Hazard Severity:** {hazards_dict['Flood Risk']:.1f} / 100")
    st.markdown(f"**Description:** {HAZARD_DESCRIPTIONS['Flood Risk']}")
    st.info("🌊 **Physical Vulnerability Drivers**: Low coastal elevation, proximity to major river basins, high astronomical king tides, and urban pluvial drainage saturation.")

with t2:
    st.markdown(f"**Hazard Severity:** {hazards_dict['Extreme Heat Risk']:.1f} / 100")
    st.markdown(f"**Description:** {HAZARD_DESCRIPTIONS['Extreme Heat Risk']}")
    st.info("🌡️ **Physical Vulnerability Drivers**: Wet-bulb temperatures exceeding 31°C, continuous heatwaves > 5 consecutive days, cooling tower thermal efficiency loss, and electrical substation derating.")

with t3:
    st.markdown(f"**Hazard Severity:** {hazards_dict['Drought Risk']:.1f} / 100")
    st.markdown(f"**Description:** {HAZARD_DESCRIPTIONS['Drought Risk']}")
    st.info("🏜️ **Physical Vulnerability Drivers**: Negative Palmer Drought Severity Index (PDSI < -3.0), groundwater aquifer depletion, agricultural irrigation quotas, and inland waterway shipping draft reductions.")

with t4:
    st.markdown(f"**Hazard Severity:** {hazards_dict['Wildfire Risk']:.1f} / 100")
    st.markdown(f"**Description:** {HAZARD_DESCRIPTIONS['Wildfire Risk']}")
    st.info("🔥 **Physical Vulnerability Drivers**: High Fire Weather Index (FWI), prolonged dry fuel moisture (< 8%), high ambient winds, and Wildland-Urban Interface (WUI) proximity.")

with t5:
    st.markdown(f"**Hazard Severity:** {hazards_dict['Heavy Rainfall Risk']:.1f} / 100")
    st.markdown(f"**Description:** {HAZARD_DESCRIPTIONS['Heavy Rainfall Risk']}")
    st.info("🌧️ **Physical Vulnerability Drivers**: 95th percentile acute precipitation (> 100mm in 24 hours), atmospheric river events, Flash Flood Guidance exceedance, and foundation seepage.")

# Historical Disaster Logs Table
st.markdown("### 📜 Regional Historical Climate Hazard Benchmark Log")
hist_city = df_hist[df_hist["city"] == city]
if hist_city.empty:
    hist_city = df_hist.head(8)
    st.caption(f"No specific local historical disasters recorded for {city}. Displaying recent global climate hazard benchmark records:")
else:
    st.caption(f"Historical climate hazard and acute disaster records recorded in {city} region (2004–2024):")

st.dataframe(
    hist_city[[
        "record_id", "year", "hazard_type", "severity_index",
        "direct_loss_usd_m", "facility_downtime_days", "supply_chain_disrupted"
    ]].reset_index(drop=True),
    use_container_width=True,
    column_config={
        "record_id": "Event ID",
        "year": "Year",
        "hazard_type": "Hazard Type",
        "severity_index": st.column_config.ProgressColumn("Severity (0-100)", min_value=0, max_value=100),
        "direct_loss_usd_m": st.column_config.NumberColumn("Economic Loss ($M)", format="$%.2fM"),
        "facility_downtime_days": st.column_config.NumberColumn("Facility Downtime (Days)", format="%d d"),
        "supply_chain_disrupted": st.column_config.CheckboxColumn("Supply Chain Disrupted")
    }
)
