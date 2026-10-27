"""
Unit tests for Climate Risk Scoring Engine.
Verifies IPCC AR6 composite hazard, vulnerability, and risk scoring logic.
"""

import pytest
from src.risk_scoring import (
    compute_composite_hazard_score,
    apply_scenario_projection,
    calculate_adaptive_capacity,
    calculate_sector_sensitivity,
    compute_vulnerability_index,
    calculate_overall_climate_risk,
)


def test_composite_hazard_score_bounds():
    hazards = {
        "Flood Risk": 80.0,
        "Extreme Heat Risk": 70.0,
        "Drought Risk": 60.0,
        "Wildfire Risk": 40.0,
        "Heavy Rainfall Risk": 90.0,
    }
    score = compute_composite_hazard_score(hazards)
    assert 0.0 <= score <= 100.0
    assert 65.0 <= score <= 75.0


def test_composite_hazard_all_zeros_and_hundreds():
    zeros = {h: 0.0 for h in ["Flood Risk", "Extreme Heat Risk", "Drought Risk", "Wildfire Risk", "Heavy Rainfall Risk"]}
    hundreds = {h: 100.0 for h in ["Flood Risk", "Extreme Heat Risk", "Drought Risk", "Wildfire Risk", "Heavy Rainfall Risk"]}
    
    assert compute_composite_hazard_score(zeros) == 0.0
    assert compute_composite_hazard_score(hundreds) == 100.0


def test_scenario_projection():
    base = 50.0
    proj_2030 = apply_scenario_projection(base, "SSP2-4.5 (Middle of the Road - Current Policy)", "2030")
    proj_2050 = apply_scenario_projection(base, "SSP2-4.5 (Middle of the Road - Current Policy)", "2050")
    
    assert proj_2030 > base
    assert proj_2050 > proj_2030
    assert proj_2050 <= 100.0


def test_adaptive_capacity_cumulative():
    cap_none = calculate_adaptive_capacity(False, False, False)
    cap_one = calculate_adaptive_capacity(True, False, False)
    cap_all = calculate_adaptive_capacity(True, True, True)
    
    assert cap_none == 0.0
    assert cap_one == 0.35
    assert cap_all == 1.0


def test_vulnerability_index_mitigation():
    hazards = {h: 70.0 for h in ["Flood Risk", "Extreme Heat Risk", "Drought Risk", "Wildfire Risk", "Heavy Rainfall Risk"]}
    sector = "Data Centers & IT Infrastructure"
    
    vuln_unmitigated = compute_vulnerability_index(sector, hazards, False, False, False)
    vuln_mitigated = compute_vulnerability_index(sector, hazards, True, True, True)
    
    # Adaptive capacity must strictly reduce vulnerability
    assert vuln_mitigated < vuln_unmitigated


def test_calculate_overall_climate_risk():
    hazards = {
        "Flood Risk": 90.0,
        "Extreme Heat Risk": 85.0,
        "Drought Risk": 40.0,
        "Wildfire Risk": 30.0,
        "Heavy Rainfall Risk": 95.0,
    }
    score, tier, color = calculate_overall_climate_risk(
        hazards,
        sector="Manufacturing & Heavy Industrial",
        has_backup_power=False,
        has_flood_barrier=False,
        has_water_recycling=False
    )
    assert 0.0 <= score <= 100.0
    assert tier in ["High", "Critical"]
    assert color.startswith("#")
