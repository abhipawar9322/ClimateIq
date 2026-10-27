"""
Transparent Climate Risk Scoring Engine.
Implements the IPCC AR6 Risk Framework: Risk = Hazard x Exposure x Vulnerability.
Provides deterministic, explainable calculations with configurable weights and scenario multipliers.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from src.config import (
    DEFAULT_HAZARD_WEIGHTS,
    SCENARIOS,
    SECTOR_VULNERABILITIES,
    RISK_TIERS,
    HAZARDS
)


def compute_composite_hazard_score(
    hazards_dict: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculates weighted composite hazard score (0 - 100).
    
    Args:
        hazards_dict: Dictionary mapping hazard names to values [0-100].
        weights: Optional custom weights mapping. Defaults to DEFAULT_HAZARD_WEIGHTS.
        
    Returns:
        Weighted score bounded between 0.0 and 100.0.
    """
    if weights is None:
        weights = DEFAULT_HAZARD_WEIGHTS

    # Normalize weights so sum is 1.0
    total_w = sum(weights.values())
    norm_w = {k: v / total_w for k, v in weights.items()}

    score = 0.0
    for hazard, weight in norm_w.items():
        val = hazards_dict.get(hazard, 0.0)
        score += val * weight

    return float(np.clip(score, 0.0, 100.0))


def apply_scenario_projection(
    baseline_hazard: float,
    scenario_name: str,
    target_year: str = "2040"
) -> float:
    """
    Projects a hazard metric into future time horizons under chosen IPCC SSP pathway.
    
    Args:
        baseline_hazard: Current baseline hazard index [0 - 100].
        scenario_name: One of the SSP scenarios configured in config.py.
        target_year: '2030', '2040', or '2050'.
        
    Returns:
        Projected hazard index [0 - 100].
    """
    scenario_data = SCENARIOS.get(scenario_name)
    if not scenario_data:
        return float(baseline_hazard)

    multipliers = scenario_data.get("multipliers", {})
    mult = multipliers.get(str(target_year), 1.0)
    projected = baseline_hazard * mult
    return float(np.clip(projected, 0.0, 100.0))


def calculate_adaptive_capacity(
    has_backup_power: bool,
    has_flood_barrier: bool,
    has_water_recycling: bool
) -> float:
    """
    Calculates adaptive capacity index between 0.0 (unmitigated) and 1.0 (fully defended).
    Weights: Backup power (35%), Flood barrier (35%), Water recycling (30%).
    """
    cap = 0.0
    if has_backup_power:
        cap += 0.35
    if has_flood_barrier:
        cap += 0.35
    if has_water_recycling:
        cap += 0.30
    return float(np.clip(cap, 0.0, 1.0))


def calculate_sector_sensitivity(
    sector: str,
    hazards_dict: Dict[str, float]
) -> float:
    """
    Computes industry-specific sensitivity weight based on sector vulnerabilities to active hazards.
    """
    sector_weights = SECTOR_VULNERABILITIES.get(
        sector,
        {h: 0.70 for h in HAZARDS}
    )
    
    # Weighted sensitivity based on hazard intensities
    weighted_sens = 0.0
    total_intensity = 0.0
    
    for h in HAZARDS:
        intensity = hazards_dict.get(h, 0.0)
        coef = sector_weights.get(h, 0.70)
        weighted_sens += intensity * coef
        total_intensity += max(intensity, 1.0)
        
    avg_sensitivity = weighted_sens / total_intensity
    return float(np.clip(avg_sensitivity, 0.20, 1.0))


def compute_vulnerability_index(
    sector: str,
    hazards_dict: Dict[str, float],
    has_backup_power: bool,
    has_flood_barrier: bool,
    has_water_recycling: bool
) -> float:
    """
    Calculates asset vulnerability index (0.0 to 1.0).
    V = Sensitivity x (1.0 - 0.70 x Adaptive Capacity)
    Adaptive defenses mitigate up to 70% of baseline sensitivity.
    """
    sensitivity = calculate_sector_sensitivity(sector, hazards_dict)
    adaptive_cap = calculate_adaptive_capacity(has_backup_power, has_flood_barrier, has_water_recycling)
    
    # Net vulnerability factor
    vuln_factor = sensitivity * (1.0 - (0.70 * adaptive_cap))
    return float(np.clip(vuln_factor, 0.05, 1.0))


def calculate_overall_climate_risk(
    hazards_dict: Dict[str, float],
    sector: str,
    has_backup_power: bool,
    has_flood_barrier: bool,
    has_water_recycling: bool,
    hazard_weights: Optional[Dict[str, float]] = None
) -> Tuple[float, str, str]:
    """
    Calculates final composite climate risk score (0 - 100), tier label, and badge color.
    Formula: Risk Score = Composite Hazard * (0.35 + 0.65 * Vulnerability Factor)
    
    Returns:
        (risk_score, tier_name, tier_color)
    """
    comp_hazard = compute_composite_hazard_score(hazards_dict, hazard_weights)
    vuln_factor = compute_vulnerability_index(
        sector,
        hazards_dict,
        has_backup_power,
        has_flood_barrier,
        has_water_recycling
    )
    
    # Composite risk combines hazard intensity modulated by vulnerability
    final_score = comp_hazard * (0.35 + 0.65 * vuln_factor)
    final_score = float(np.clip(final_score, 0.0, 100.0))
    
    tier_name = "Low"
    tier_color = RISK_TIERS["Low"]["color"]
    
    for name, info in RISK_TIERS.items():
        low_bound, high_bound = info["range"]
        if low_bound <= final_score <= high_bound:
            tier_name = name
            tier_color = info["color"]
            break
            
    return round(final_score, 1), tier_name, tier_color


def score_facility_row(
    row: pd.Series,
    scenario_name: Optional[str] = None,
    target_year: str = "2040"
) -> Dict[str, Any]:
    """
    Convenience method to score a single facility row from the DataFrame.
    """
    hazards = {
        "Flood Risk": float(row.get("flood_hazard", 50.0)),
        "Extreme Heat Risk": float(row.get("heat_hazard", 50.0)),
        "Drought Risk": float(row.get("drought_hazard", 50.0)),
        "Wildfire Risk": float(row.get("wildfire_hazard", 50.0)),
        "Heavy Rainfall Risk": float(row.get("rainfall_hazard", 50.0)),
    }
    
    # If a climate scenario is specified, project hazards
    if scenario_name:
        hazards = {
            k: apply_scenario_projection(v, scenario_name, target_year)
            for k, v in hazards.items()
        }
        
    sector = str(row.get("sector", "Manufacturing & Heavy Industrial"))
    bk_pwr = bool(row.get("backup_power", False))
    fl_bar = bool(row.get("flood_barrier", False))
    wt_rec = bool(row.get("water_recycling", False))
    
    comp_hazard = compute_composite_hazard_score(hazards)
    vuln = compute_vulnerability_index(sector, hazards, bk_pwr, fl_bar, wt_rec)
    risk_score, tier, color = calculate_overall_climate_risk(hazards, sector, bk_pwr, fl_bar, wt_rec)
    
    return {
        "composite_hazard": round(comp_hazard, 1),
        "vulnerability_factor": round(vuln, 2),
        "overall_risk_score": risk_score,
        "risk_tier": tier,
        "tier_color": color,
        "hazards": hazards
    }
