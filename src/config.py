"""
ClimateIQ Configuration and Constants.
Defines color schemes, risk thresholds, hazard weights, IPCC scenarios, and industry profiles.
"""

from typing import Dict, List, Any

# ==============================================================================
# 1. UI & DESIGN SYSTEM PALETTE
# ==============================================================================
THEME_COLORS = {
    "primary_dark_green": "#0F4C3A",
    "forest_green": "#1B4332",
    "emerald": "#2D6A4F",
    "mint": "#52B788",
    "slate_blue": "#1D3557",
    "teal": "#2A9D8F",
    "light_bg": "#F8FBF9",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text_primary": "#1A202C",
    "text_secondary": "#4A5568",
    "text_muted": "#718096",
}

RISK_TIERS = {
    "Low": {
        "range": (0.0, 25.0),
        "color": "#2A9D8F",
        "badge": "LOW RISK",
        "description": "Minimal operational threat. Standard continuous monitoring recommended."
    },
    "Moderate": {
        "range": (25.1, 50.0),
        "color": "#E9C46A",
        "badge": "MODERATE RISK",
        "description": "Manageable exposure. Preventative retrofits and supply redundancies advised."
    },
    "High": {
        "range": (50.1, 75.0),
        "color": "#F4A261",
        "badge": "HIGH RISK",
        "description": "Substantial hazard. Capital-intensive mitigation and insurance restructuring required."
    },
    "Critical": {
        "range": (75.1, 100.0),
        "color": "#E63946",
        "badge": "CRITICAL RISK",
        "description": "Severe vulnerability. Immediate resilience investments or asset relocation study warranted."
    }
}

# ==============================================================================
# 2. HAZARDS & IPCC METHODOLOGY
# ==============================================================================
HAZARDS: List[str] = [
    "Flood Risk",
    "Extreme Heat Risk",
    "Drought Risk",
    "Wildfire Risk",
    "Heavy Rainfall Risk"
]

HAZARD_ICONS: Dict[str, str] = {
    "Flood Risk": "🌊",
    "Extreme Heat Risk": "🌡️",
    "Drought Risk": "🏜️",
    "Wildfire Risk": "🔥",
    "Heavy Rainfall Risk": "🌧️",
    "Overall Risk": "🌐"
}

HAZARD_DESCRIPTIONS: Dict[str, str] = {
    "Flood Risk": "Riverine inundation, storm surge, coastal tidal flooding, and pluvial pooling.",
    "Extreme Heat Risk": "Heatwave duration, wet-bulb temperature stress, and excessive cooling degree days.",
    "Drought Risk": "Prolonged soil moisture deficits, precipitation deficits, and reservoir drawdown.",
    "Wildfire Risk": "Fuel dryness, high fire weather indices (FWI), and urban-wildland interface proximity.",
    "Heavy Rainfall Risk": "95th percentile acute precipitation events and flash flood drainage exceedance."
}

# Default multi-criteria weighting for overall hazard index
DEFAULT_HAZARD_WEIGHTS: Dict[str, float] = {
    "Flood Risk": 0.25,
    "Extreme Heat Risk": 0.20,
    "Drought Risk": 0.18,
    "Wildfire Risk": 0.17,
    "Heavy Rainfall Risk": 0.20
}

# IPCC AR6 Shared Socioeconomic Pathways (SSP) Multipliers relative to 2024 Baseline
SCENARIOS: Dict[str, Dict[str, Any]] = {
    "SSP1-2.6 (Paris Aligned - Low Warming)": {
        "code": "SSP1-2.6",
        "temp_target": "+1.5°C to 1.8°C by 2100",
        "description": "Rapid global decarbonization, strict sustainability transitions, minimal long-term escalation.",
        "multipliers": {
            "2030": 1.08,
            "2040": 1.15,
            "2050": 1.20
        }
    },
    "SSP2-4.5 (Middle of the Road - Current Policy)": {
        "code": "SSP2-4.5",
        "temp_target": "+2.7°C by 2100",
        "description": "Intermediate greenhouse pathway where current policy commitments persist with moderate adaptation.",
        "multipliers": {
            "2030": 1.15,
            "2040": 1.32,
            "2050": 1.48
        }
    },
    "SSP5-8.5 (Fossil-Fueled Development - High Risk)": {
        "code": "SSP5-8.5",
        "temp_target": "+4.4°C by 2100",
        "description": "Continued fossil-fuel dependency, high GHG emissions, catastrophic unmitigated climate acceleration.",
        "multipliers": {
            "2030": 1.25,
            "2040": 1.58,
            "2050": 1.92
        }
    }
}

# ==============================================================================
# 3. INDUSTRY SECTORS & VULNERABILITY COEFFICIENTS
# ==============================================================================
SECTOR_VULNERABILITIES: Dict[str, Dict[str, float]] = {
    "Data Centers & IT Infrastructure": {
        "Flood Risk": 0.85,
        "Extreme Heat Risk": 0.95,  # Cooling energy spikes & thermal throttle
        "Drought Risk": 0.60,       # Water cooling constraints
        "Wildfire Risk": 0.50,      # Air particulate filtration
        "Heavy Rainfall Risk": 0.70,
        "base_downtime_cost_per_day": 280000,  # USD
        "worker_density": 0.3
    },
    "Manufacturing & Heavy Industrial": {
        "Flood Risk": 0.90,
        "Extreme Heat Risk": 0.70,
        "Drought Risk": 0.80,       # Industrial process water
        "Wildfire Risk": 0.65,
        "Heavy Rainfall Risk": 0.80,
        "base_downtime_cost_per_day": 350000,  # USD
        "worker_density": 0.7
    },
    "Agriculture & Food Supply": {
        "Flood Risk": 0.95,
        "Extreme Heat Risk": 0.90,
        "Drought Risk": 1.00,       # Crop failure & livestock stress
        "Wildfire Risk": 0.85,
        "Heavy Rainfall Risk": 0.85,
        "base_downtime_cost_per_day": 95000,   # USD
        "worker_density": 0.8
    },
    "Logistics, Ports & Warehousing": {
        "Flood Risk": 1.00,         # Harbor/dock inundation
        "Extreme Heat Risk": 0.60,
        "Drought Risk": 0.40,       # Low river freight levels
        "Wildfire Risk": 0.55,
        "Heavy Rainfall Risk": 0.90,
        "base_downtime_cost_per_day": 420000,  # USD
        "worker_density": 0.6
    },
    "Commercial Real Estate & Hospitality": {
        "Flood Risk": 0.80,
        "Extreme Heat Risk": 0.75,
        "Drought Risk": 0.35,
        "Wildfire Risk": 0.75,
        "Heavy Rainfall Risk": 0.75,
        "base_downtime_cost_per_day": 180000,  # USD
        "worker_density": 0.5
    },
    "Renewable Energy & Utilities": {
        "Flood Risk": 0.75,
        "Extreme Heat Risk": 0.80,  # Transmission line sag & solar panel derating
        "Drought Risk": 0.90,       # Hydroelectric deficiency
        "Wildfire Risk": 0.90,      # Power line ignition & smoke blocking solar
        "Heavy Rainfall Risk": 0.70,
        "base_downtime_cost_per_day": 500000,  # USD
        "worker_density": 0.4
    }
}
