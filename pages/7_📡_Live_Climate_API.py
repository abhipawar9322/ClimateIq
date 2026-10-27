"""
Live Climate API & Real-Time Weather Monitor — ClimateIQ.
Queries Open-Meteo free public climate endpoints for live meteorological indicators,
providing heat index stress calculation and seamless offline fallback to local benchmarks.
"""

import streamlit as st
import pandas as pd
from src.ui_helpers import (
    apply_custom_styles,
    render_sidebar_brand,
    render_page_header,
    render_metric_card
)
from src.api_client import fetch_live_city_weather
from src.data_loader import load_locations_data
from src.config import THEME_COLORS

st.set_page_config(page_title="Live Climate API | ClimateIQ", page_icon="📡", layout="wide")
apply_custom_styles()
render_sidebar_brand()

render_page_header(
    title="Real-Time Climate & Weather Monitor",
    subtitle="Live atmospheric stress telemetry via Open-Meteo API with heat index calculation and offline fallback.",
    icon="📡"
)

# Search & Presets
st.markdown("### 🔍 Query Live Weather & Meteorological Stress")

col_search, col_btn = st.columns([3, 1])
with col_search:
    city_input = st.text_input("Enter Global City Name", value="Singapore", help="Type any city worldwide to query live climate data.")

st.markdown("**Quick Global Enterprise Hub Presets:**")
presets = ["Mumbai", "New York", "Rotterdam", "Tokyo", "Houston", "Frankfurt", "Dubai", "Sydney", "London"]
preset_cols = st.columns(len(presets))

for i, p_city in enumerate(presets):
    if preset_cols[i].button(p_city, use_container_width=True):
        city_input = p_city

# Query API
with st.spinner(f"Querying live atmospheric telemetry for {city_input}..."):
    weather_data = fetch_live_city_weather(city_input)

if weather_data.get("success"):
    st.success(f"🟢 **LIVE TELEMETRY ACTIVE**: Received live satellite & meteorological readings for {weather_data['city']}, {weather_data['country']}.")
    
    # Live KPI Cards
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        render_metric_card("Live Temperature", f"{weather_data['temperature_c']} °C", f"Elevation: {weather_data['elevation_m']} m")
    with w2:
        render_metric_card("Relative Humidity", f"{weather_data['humidity_pct']}%", f"Wind: {weather_data['wind_speed_kmh']} km/h")
    with w3:
        heat_idx = weather_data['heat_index_c']
        heat_color = "#E63946" if heat_idx > 38 else ("#F4A261" if heat_idx > 32 else "#2A9D8F")
        render_metric_card("Calculated Heat Index", f"{heat_idx:.1f} °C", "Wet-bulb / thermal stress", delta_color=heat_color)
    with w4:
        precip = weather_data['precipitation_mm']
        precip_delta = "Acute Storm Threat" if precip > 15 else "Normal Precipitation"
        render_metric_card("Current Precipitation", f"{precip} mm/h", precip_delta)

    st.markdown("---")
    
    # Meteorological Details Card
    st.markdown("### 📊 Atmospheric Stress Indicators")
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-weight: 700; font-size: 1.15rem; color: #0F4C3A;">Coordinates: {weather_data['latitude']}° N, {weather_data['longitude']}° E</div>
                <span class="risk-badge badge-{'critical' if heat_idx > 38 or precip > 20 else 'low'}">Telemetry Status: Synchronized</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; font-size: 0.9rem; color: #4A5568;">
                <div><b>24h Max Forecast Temp:</b> {weather_data['daily_max_temp_c']} °C</div>
                <div><b>24h Forecast Precipitation:</b> {weather_data['daily_precip_sum_mm']} mm</div>
                <div><b>Wind Speed:</b> {weather_data['wind_speed_kmh']} km/h</div>
                <div><b>Elevation:</b> {weather_data['elevation_m']} meters MSL</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    # Offline Fallback Mode
    st.warning(f"⚠️ {weather_data.get('error_message')}")
    st.info("Switching seamlessly to pre-compiled verified offline regional benchmarks:")
    
    df_loc = load_locations_data()
    loc_match = df_loc[df_loc["city"].str.lower() == city_input.lower()]
    
    if not loc_match.empty:
        row = loc_match.iloc[0]
        st.markdown(f"#### 📍 Offline Benchmark for **{row['city']}, {row['country']}**")
        fb1, fb2, fb3, fb4 = st.columns(4)
        with fb1:
            render_metric_card("Elevation", f"{row['elevation_m']} m", "Offline Geo Model")
        with fb2:
            render_metric_card("Distance to Coast", f"{row['distance_to_coast_km']} km", "Tidal Risk Factor")
        with fb3:
            render_metric_card("Flood Baseline", f"{row['flood_hazard']:.1f} / 100", "Baseline Hazard")
        with fb4:
            render_metric_card("Extreme Heat Baseline", f"{row['heat_hazard']:.1f} / 100", "Baseline Hazard")
    else:
        st.write("Browse available cities with offline benchmarks:")
        st.dataframe(df_loc[["city", "country", "climate_zone", "flood_hazard", "heat_hazard", "rainfall_hazard"]], use_container_width=True)
