"""
UI Helper functions and Shared Styles for ClimateIQ.
Provides custom CSS injection, executive branding banners, metric card renderers,
and persistent session state management across pages.
"""

from typing import Dict, Any, Optional
import streamlit as st
from src.config import THEME_COLORS, RISK_TIERS


def apply_custom_styles() -> None:
    """Injects modern, enterprise-grade CSS into the Streamlit session."""
    st.markdown(
        f"""
        <style>
        /* Base typography & page padding */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {THEME_COLORS["text_primary"]};
        }}
        
        /* Main background */
        .stApp {{
            background-color: {THEME_COLORS["light_bg"]};
        }}
        
        /* Metric Card Container */
        .metric-card {{
            background: #FFFFFF;
            border-radius: 10px;
            padding: 18px 20px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 4px rgba(15, 76, 58, 0.04);
            margin-bottom: 12px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(15, 76, 58, 0.08);
            transform: translateY(-2px);
        }}
        
        .metric-label {{
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {THEME_COLORS["text_muted"]};
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .metric-value {{
            font-size: 1.85rem;
            font-weight: 700;
            color: {THEME_COLORS["primary_dark_green"]};
            line-height: 1.2;
        }}
        
        .metric-delta {{
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 4px;
        }}
        
        /* Badges */
        .risk-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .badge-low {{ background: #D8F3DC; color: #1B4332; }}
        .badge-moderate {{ background: #FEF3C7; color: #92400E; }}
        .badge-high {{ background: #FFEDD5; color: #9A3412; }}
        .badge-critical {{ background: #FEE2E2; color: #991B1B; }}
        
        /* Header Banner */
        .page-header {{
            background: linear-gradient(135deg, #0F4C3A 0%, #1D3557 100%);
            color: #FFFFFF;
            padding: 24px 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(15, 76, 58, 0.15);
        }}
        .page-header h1 {{
            color: #FFFFFF;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }}
        .page-header p {{
            color: #E2E8F0;
            font-size: 0.95rem;
            margin: 0;
            opacity: 0.95;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: #F1F6F3;
            border-right: 1px solid #D8E2DC;
        }}
        
        /* Buttons */
        .stButton>button {{
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            font-weight: 600;
            color: {THEME_COLORS["primary_dark_green"]};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_sidebar_brand() -> None:
    """Renders the executive ClimateIQ brand header and version badge in the sidebar."""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #D8E2DC; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.8rem;">🌿</span>
                    <div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: {THEME_COLORS["primary_dark_green"]}; letter-spacing: -0.02em;">ClimateIQ</div>
                        <div style="font-size: 0.72rem; font-weight: 600; color: {THEME_COLORS["teal"]}; text-transform: uppercase; letter-spacing: 0.08em;">Risk Intelligence</div>
                    </div>
                </div>
                <div style="display: flex; gap: 6px; margin-top: 10px;">
                    <span style="background: #E2E8F0; color: #334155; font-size: 0.68rem; padding: 2px 6px; border-radius: 4px; font-weight: 600;">v2.4 Enterprise</span>
                    <span style="background: #D8F3DC; color: #1B4332; font-size: 0.68rem; padding: 2px 6px; border-radius: 4px; font-weight: 600;">IPCC AR6</span>
                    <span style="background: #E0E7FF; color: #3730A3; font-size: 0.68rem; padding: 2px 6px; border-radius: 4px; font-weight: 600;">TCFD Aligned</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_page_header(title: str, subtitle: str, icon: str = "🌐") -> None:
    """Renders a top page header banner with dark green-blue gradient."""
    st.markdown(
        f"""
        <div class="page-header">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.2rem;">{icon}</span>
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(label: str, value: str, delta: Optional[str] = None, delta_color: str = "#2A9D8F") -> None:
    """Renders a clean styled executive metric card."""
    delta_html = f'<div class="metric-delta" style="color: {delta_color};">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def get_risk_badge_html(tier: str) -> str:
    """Returns HTML for color-coded risk badge."""
    tier_lower = tier.lower()
    return f'<span class="risk-badge badge-{tier_lower}">{tier} Risk</span>'
