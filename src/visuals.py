"""
Visualization Components for ClimateIQ.
Generates enterprise-grade, interactive Plotly figures:
- Global Portfolio Geo-Maps
- Multi-Hazard Radar / Spider Charts
- Semi-circular Risk Tier Gauges
- Scenario Trajectory Projections
- Financial Loss Waterfall Breakdown
- ML Model Diagnostics & Feature Importance Plots
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.config import THEME_COLORS, RISK_TIERS, HAZARDS


def get_tier_color(score: float) -> str:
    """Helper to retrieve color hex for given score."""
    if score <= 25:
        return RISK_TIERS["Low"]["color"]
    elif score <= 50:
        return RISK_TIERS["Moderate"]["color"]
    elif score <= 75:
        return RISK_TIERS["High"]["color"]
    return RISK_TIERS["Critical"]["color"]


def create_global_risk_map(df_facilities: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive world map of corporate facilities colored by risk tier
    with bubble size scaled by asset value.
    """
    # Color mapping
    color_map = {tier: data["color"] for tier, data in RISK_TIERS.items()}
    
    fig = px.scatter_geo(
        df_facilities,
        lat="latitude",
        lon="longitude",
        hover_name="facility_name",
        hover_data={
            "city": True,
            "country": True,
            "sector": True,
            "overall_risk_score": ":.1f",
            "risk_tier": True,
            "asset_value_m": ":$,.1fM",
            "latitude": False,
            "longitude": False
        },
        size="asset_value_m",
        color="risk_tier",
        color_discrete_map=color_map,
        size_max=24,
        projection="natural earth",
        title="<b>Global Enterprise Asset Distribution & Climate Vulnerability</b>"
    )
    
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        showland=True,
        landcolor="#F1F5F9",
        showocean=True,
        oceancolor="#E2E8F0",
        showlakes=True,
        lakecolor="#E2E8F0",
        showcountries=True,
        countrycolor="#CBD5E1",
        resolution=110
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=dict(text="<b>Risk Classification: </b>")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=520,
        font=dict(family="sans-serif", size=12, color=THEME_COLORS["text_primary"])
    )
    
    return fig


def create_risk_gauge(score: float, title: str = "Overall Risk Index") -> go.Figure:
    """
    Renders a semi-circular gauge with color-coded risk bands and needle indicator.
    """
    tier_color = get_tier_color(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b>", 'font': {'size': 18, 'color': THEME_COLORS["primary_dark_green"]}},
        number={'suffix': "/100", 'font': {'size': 32, 'color': tier_color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': THEME_COLORS["text_muted"]},
            'bar': {'color': tier_color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': THEME_COLORS["border"],
            'steps': [
                {'range': [0, 25], 'color': '#D8F3DC'},
                {'range': [25, 50], 'color': '#FFF3B0'},
                {'range': [50, 75], 'color': '#FCE4D6'},
                {'range': [75, 100], 'color': '#FAD2E1'}
            ],
            'threshold': {
                'line': {'color': tier_color, 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif")
    )
    return fig


def create_multi_hazard_radar(hazards_dict: Dict[str, float], benchmark_dict: Optional[Dict[str, float]] = None) -> go.Figure:
    """
    Renders a radar (spider) chart comparing asset hazard exposures against benchmark average.
    """
    categories = list(hazards_dict.keys())
    values = [hazards_dict[c] for c in categories]
    # Close the polygon
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()
    
    # Asset trace
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(15, 76, 58, 0.25)',
        line=dict(color=THEME_COLORS["primary_dark_green"], width=2.5),
        name='Facility Exposure'
    ))
    
    # Optional portfolio average benchmark
    if benchmark_dict:
        bench_vals = [benchmark_dict.get(c, 50.0) for c in categories]
        bench_vals_closed = bench_vals + [bench_vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=bench_vals_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor='rgba(42, 157, 143, 0.1)',
            line=dict(color=THEME_COLORS["teal"], width=1.5, dash='dash'),
            name='Global Benchmark'
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=THEME_COLORS["text_muted"])
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=THEME_COLORS["text_primary"], family="sans-serif")
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.2),
        margin=dict(l=40, r=40, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        height=340
    )
    return fig


def create_hazard_breakdown_bars(hazards_dict: Dict[str, float]) -> go.Figure:
    """
    Renders horizontal bars for each hazard with individual tier coloring.
    """
    hazards = list(hazards_dict.keys())
    scores = [hazards_dict[h] for h in hazards]
    colors = [get_tier_color(s) for s in scores]
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=hazards,
        orientation='h',
        marker=dict(color=colors, line=dict(color=THEME_COLORS["border"], width=1)),
        text=[f"{s:.1f}/100" for s in scores],
        textposition='inside',
        insidetextanchor='end',
        textfont=dict(color="white", size=12, family="sans-serif")
    ))
    
    fig.add_vline(x=25, line_width=1, line_dash="dot", line_color=RISK_TIERS["Low"]["color"])
    fig.add_vline(x=50, line_width=1, line_dash="dot", line_color=RISK_TIERS["Moderate"]["color"])
    fig.add_vline(x=75, line_width=1, line_dash="dot", line_color=RISK_TIERS["High"]["color"])
    
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Hazard Severity Score (0 - 100)"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280
    )
    return fig


def create_scenario_projection_chart(baseline_score: float) -> go.Figure:
    """
    Plots projected hazard trajectory across 2024 (present), 2030, 2040, and 2050
    under SSP1-2.6, SSP2-4.5, and SSP5-8.5.
    """
    years = [2024, 2030, 2040, 2050]
    
    ssp1_vals = [
        baseline_score,
        min(100, baseline_score * 1.08),
        min(100, baseline_score * 1.15),
        min(100, baseline_score * 1.20)
    ]
    ssp2_vals = [
        baseline_score,
        min(100, baseline_score * 1.15),
        min(100, baseline_score * 1.32),
        min(100, baseline_score * 1.48)
    ]
    ssp5_vals = [
        baseline_score,
        min(100, baseline_score * 1.25),
        min(100, baseline_score * 1.58),
        min(100, baseline_score * 1.92)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=ssp1_vals,
        mode='lines+markers',
        name='SSP1-2.6 (Paris Low Carbon)',
        line=dict(color='#2A9D8F', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=ssp2_vals,
        mode='lines+markers',
        name='SSP2-4.5 (Middle of the Road)',
        line=dict(color='#E9C46A', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=ssp5_vals,
        mode='lines+markers',
        name='SSP5-8.5 (Fossil High Emissions)',
        line=dict(color='#E63946', width=3, dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="<b>Projected Risk Trajectory Across IPCC AR6 Climate Pathways</b>",
        xaxis=dict(title="Time Horizon Year", tickmode='array', tickvals=years),
        yaxis=dict(title="Projected Severity Index", range=[0, 105]),
        margin=dict(l=30, r=20, t=50, b=30),
        legend=dict(orientation="h", y=-0.2, x=0.1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FAFCFB",
        height=360
    )
    return fig


def create_financial_loss_waterfall(impact_dict: Dict[str, Any]) -> go.Figure:
    """
    Renders waterfall breakdown of total expected annual climate loss.
    """
    phys_loss = impact_dict.get("expected_physical_loss_m", 0.0)
    rev_loss = impact_dict.get("revenue_at_risk_m", 0.0)
    workforce_loss = impact_dict.get("workforce_cost_m", 0.0)
    total_var = impact_dict.get("total_climate_var_m", 0.0)
    
    fig = go.Figure(go.Waterfall(
        name="Loss Components",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Physical Asset Damage", "Business Interruption", "Workforce Disruption", "Total Climate VaR"],
        textposition="outside",
        text=[f"${phys_loss:.2f}M", f"${rev_loss:.2f}M", f"${workforce_loss:.2f}M", f"${total_var:.2f}M"],
        y=[phys_loss, rev_loss, workforce_loss, total_var],
        connector={"line": {"color": THEME_COLORS["border"]}},
        decreasing={"marker": {"color": THEME_COLORS["teal"]}},
        increasing={"marker": {"color": THEME_COLORS["slate_blue"]}},
        totals={"marker": {"color": THEME_COLORS["primary_dark_green"]}}
    ))
    
    fig.update_layout(
        title="<b>Annual Climate Value-at-Risk (VaR) Breakdown ($ Millions)</b>",
        yaxis=dict(title="Estimated Impact ($M USD)"),
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FAFCFB",
        height=340
    )
    return fig


def create_feature_importance_plot(feat_importances: List[Tuple[str, float]], top_n: int = 10) -> go.Figure:
    """
    Renders horizontal bar chart of top ML feature importances.
    """
    top_feats = feat_importances[:top_n][::-1]
    names = [f[0].replace("num__", "").replace("cat__", "").replace("_", " ").title() for f in top_feats]
    values = [f[1] for f in top_feats]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation='h',
        marker=dict(color=THEME_COLORS["emerald"]),
        text=[f"{v*100:.1f}%" for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="<b>Random Forest Feature Importance (Loss Ratio Driver Ranking)</b>",
        xaxis=dict(title="Relative Importance Weight", tickformat=".0%"),
        margin=dict(l=10, r=40, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350
    )
    return fig


def create_model_residuals_plot(y_true: List[float], y_pred: List[float]) -> go.Figure:
    """
    Renders actual vs predicted scatter plot for model diagnostic inspection.
    """
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    
    fig = go.Figure()
    
    # Scatter points
    fig.add_trace(go.Scatter(
        x=y_true,
        y=y_pred,
        mode='markers',
        marker=dict(color=THEME_COLORS["slate_blue"], size=7, opacity=0.8),
        name='Test Predictions'
    ))
    
    # 45-degree reference line
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        line=dict(color='#E63946', dash='dash', width=2),
        name='Perfect Fit'
    ))
    
    fig.update_layout(
        title="<b>Actual vs. Predicted Loss Ratio (% of Asset Value)</b>",
        xaxis=dict(title="Actual Loss Ratio (%)"),
        yaxis=dict(title="Predicted Loss Ratio (%)"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", y=-0.2, x=0.2),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FAFCFB",
        height=340
    )
    return fig
