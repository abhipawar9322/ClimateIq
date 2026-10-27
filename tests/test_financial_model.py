"""
Unit tests for Financial and Business Impact Analytics.
"""

import pytest
from src.financial_model import calculate_business_impacts, calculate_adaptation_roi


def test_calculate_business_impacts():
    hazards = {
        "Flood Risk": 75.0,
        "Extreme Heat Risk": 80.0,
        "Drought Risk": 50.0,
        "Wildfire Risk": 45.0,
        "Heavy Rainfall Risk": 70.0
    }
    
    impacts = calculate_business_impacts(
        asset_value_m=500.0,
        annual_revenue_m=250.0,
        employees=1000,
        risk_score=72.0,
        sector="Manufacturing & Heavy Industrial",
        hazards_dict=hazards,
        has_backup_power=False,
        has_flood_barrier=False,
        has_water_recycling=False
    )
    
    assert impacts["expected_physical_loss_m"] > 0
    assert impacts["downtime_days"] > 0
    assert impacts["revenue_at_risk_m"] > 0
    assert impacts["total_climate_var_m"] > impacts["expected_physical_loss_m"]
    assert impacts["insurance_surge_pct"] > 0


def test_adaptation_mitigation_benefit():
    hazards = {h: 70.0 for h in ["Flood Risk", "Extreme Heat Risk", "Drought Risk", "Wildfire Risk", "Heavy Rainfall Risk"]}
    
    unmitigated = calculate_business_impacts(
        500.0, 250.0, 1000, 70.0, "Logistics, Ports & Warehousing", hazards, False, False, False
    )
    mitigated = calculate_business_impacts(
        500.0, 250.0, 1000, 70.0, "Logistics, Ports & Warehousing", hazards, True, True, True
    )
    
    assert mitigated["downtime_days"] < unmitigated["downtime_days"]
    assert mitigated["revenue_at_risk_m"] < unmitigated["revenue_at_risk_m"]


def test_adaptation_roi():
    roi = calculate_adaptation_roi(
        current_annual_var_m=12.5,
        capex_cost_m=15.0,
        opex_annual_m=0.5,
        loss_reduction_pct=60.0,
        time_horizon_years=10,
        discount_rate=0.06
    )
    
    assert roi["annual_avoided_loss_m"] == 7.5
    assert roi["net_annual_benefit_m"] == 7.0
    assert roi["npv_m"] > 0
    assert roi["payback_years"] < 5.0
    assert roi["is_financially_viable"] is True
