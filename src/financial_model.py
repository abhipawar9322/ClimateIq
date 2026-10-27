"""
Financial and Business Impact Analytics Engine for ClimateIQ.
Estimates Expected Annual Loss (EAL), Business Interruption Downtime,
Climate Value at Risk (VaR), Worker Productivity Loss, and Adaptation ROI.
"""

from typing import Dict, Any, List
import numpy as np
from src.config import SECTOR_VULNERABILITIES


def calculate_business_impacts(
    asset_value_m: float,
    annual_revenue_m: float,
    employees: int,
    risk_score: float,
    sector: str,
    hazards_dict: Dict[str, float],
    has_backup_power: bool,
    has_flood_barrier: bool,
    has_water_recycling: bool
) -> Dict[str, Any]:
    """
    Computes comprehensive corporate financial and operational loss exposure.
    
    Args:
        asset_value_m: Total facility replacement value in Million USD.
        annual_revenue_m: Annual operating revenue in Million USD.
        employees: On-site workforce headcount.
        risk_score: Overall climate risk score [0 - 100].
        sector: Enterprise industry sector.
        hazards_dict: Breakdown of individual hazard values [0 - 100].
        has_backup_power: Presence of auxiliary power generators/microgrid.
        has_flood_barrier: Presence of physical sea/river flood barriers.
        has_water_recycling: Presence of closed-loop water treatment.
        
    Returns:
        Dictionary of financial metrics (EAL, downtime, revenue at risk, productivity loss, etc.).
    """
    sector_info = SECTOR_VULNERABILITIES.get(
        sector,
        {"base_downtime_cost_per_day": 250000, "worker_density": 0.5}
    )
    
    # 1. Expected Physical Damage Ratio (%)
    # Non-linear cubic power curve reflecting acute stress thresholds
    normalized_risk = risk_score / 100.0
    damage_ratio = 0.12 * (normalized_risk ** 2.2)  # up to ~12% in extreme critical cases
    expected_annual_physical_loss_m = asset_value_m * damage_ratio
    
    # 2. Estimated Annual Downtime Days
    # Base potential downtime modulated by resilience features
    defense_mitigation = (
        (0.35 if has_backup_power else 0.0) +
        (0.40 if has_flood_barrier else 0.0) +
        (0.25 if has_water_recycling else 0.0)
    )
    
    base_annual_days = 32.0 * (normalized_risk ** 1.6)
    net_downtime_days = max(0.5, base_annual_days * (1.0 - 0.70 * defense_mitigation))
    
    # 3. Revenue at Risk (Business Interruption Loss)
    daily_revenue = annual_revenue_m / 365.0
    direct_interruption_loss_m = daily_revenue * net_downtime_days
    
    # Supply chain indirect friction multiplier
    supply_chain_multiplier = 1.25 if sector in [
        "Manufacturing & Heavy Industrial",
        "Logistics, Ports & Warehousing",
        "Data Centers & IT Infrastructure"
    ] else 1.10
    total_revenue_at_risk_m = direct_interruption_loss_m * supply_chain_multiplier
    
    # 4. Worker Productivity Loss
    # Driven primarily by heat stress & wildfire air quality
    heat_score = hazards_dict.get("Extreme Heat Risk", 50.0)
    wildfire_score = hazards_dict.get("Wildfire Risk", 30.0)
    worker_density = sector_info.get("worker_density", 0.5)
    
    # Labor loss factor: heat above 65 causes thermal fatigue
    heat_stress_factor = max(0.0, (heat_score - 50.0) / 100.0) * 0.20
    smoke_stress_factor = max(0.0, (wildfire_score - 60.0) / 100.0) * 0.15
    productivity_loss_pct = (heat_stress_factor + smoke_stress_factor) * worker_density * 100.0
    
    # Estimated economic labor friction ($50k avg annual salary per employee)
    annual_payroll_m = (employees * 65000) / 1_000_000.0
    workforce_productivity_cost_m = annual_payroll_m * (productivity_loss_pct / 100.0)
    
    # 5. Total Climate Value-at-Risk (Total VaR)
    total_var_m = expected_annual_physical_loss_m + total_revenue_at_risk_m + workforce_productivity_cost_m
    
    # 6. Projected Insurance Premium Surge
    # If risk is > 50, insurance premiums see risk loadings between 25% and 120%
    base_insurance_premium_m = asset_value_m * 0.008  # standard 0.8% of asset value
    if risk_score > 75:
        premium_surge_pct = 85.0 + (risk_score - 75) * 2.5
    elif risk_score > 50:
        premium_surge_pct = 30.0 + (risk_score - 50) * 2.0
    else:
        premium_surge_pct = 5.0
    projected_annual_premium_m = base_insurance_premium_m * (1.0 + premium_surge_pct / 100.0)

    return {
        "expected_physical_loss_m": round(expected_annual_physical_loss_m, 2),
        "damage_ratio_pct": round(damage_ratio * 100.0, 2),
        "downtime_days": round(net_downtime_days, 1),
        "revenue_at_risk_m": round(total_revenue_at_risk_m, 2),
        "worker_productivity_loss_pct": round(productivity_loss_pct, 1),
        "workforce_cost_m": round(workforce_productivity_cost_m, 2),
        "total_climate_var_m": round(total_var_m, 2),
        "base_insurance_premium_m": round(base_insurance_premium_m, 2),
        "insurance_surge_pct": round(premium_surge_pct, 1),
        "projected_insurance_m": round(projected_annual_premium_m, 2),
    }


def calculate_adaptation_roi(
    current_annual_var_m: float,
    capex_cost_m: float,
    opex_annual_m: float,
    loss_reduction_pct: float = 65.0,
    time_horizon_years: int = 10,
    discount_rate: float = 0.06
) -> Dict[str, Any]:
    """
    Computes Capital Expenditure ROI and Net Present Value (NPV) for resilience adaptation investments.
    """
    annual_savings_m = current_annual_var_m * (loss_reduction_pct / 100.0)
    net_annual_benefit_m = annual_savings_m - opex_annual_m
    
    # Calculate Discounted Cash Flows (NPV)
    npv = -capex_cost_m
    cumulative_benefits = 0.0
    for year in range(1, time_horizon_years + 1):
        discount_factor = 1.0 / ((1.0 + discount_rate) ** year)
        discounted_val = net_annual_benefit_m * discount_factor
        npv += discounted_val
        cumulative_benefits += net_annual_benefit_m
        
    payback_years = (
        round(capex_cost_m / net_annual_benefit_m, 1)
        if net_annual_benefit_m > 0
        else 99.0
    )
    roi_pct = (
        round(((cumulative_benefits - capex_cost_m) / capex_cost_m) * 100.0, 1)
        if capex_cost_m > 0
        else 0.0
    )
    
    return {
        "annual_avoided_loss_m": round(annual_savings_m, 2),
        "net_annual_benefit_m": round(net_annual_benefit_m, 2),
        "npv_m": round(npv, 2),
        "payback_years": min(payback_years, 30.0),
        "roi_10yr_pct": roi_pct,
        "is_financially_viable": npv > 0
    }
