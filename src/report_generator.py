"""
Executive Report and Disclosure Summary Generator for ClimateIQ.
Generates board-ready Markdown briefs, PDF reports (via fpdf2), and CSV audit exports
aligned with TCFD (Task Force on Climate-Related Financial Disclosures) and CSRD standards.
"""

from typing import Dict, Any, List
import io
import pandas as pd
from fpdf import FPDF
from src.config import THEME_COLORS


def generate_executive_markdown_report(
    facility_data: Dict[str, Any],
    hazards_data: Dict[str, float],
    risk_summary: Dict[str, Any],
    financial_data: Dict[str, Any],
    mitigation_actions: List[Dict[str, str]]
) -> str:
    """
    Constructs an executive markdown summary of climate vulnerability and exposure.
    """
    fac_name = facility_data.get("facility_name", "Enterprise Facility")
    city = facility_data.get("city", "Global Site")
    country = facility_data.get("country", "")
    sector = facility_data.get("sector", "Industrial")
    asset_val = facility_data.get("asset_value_m", 0.0)
    score = risk_summary.get("overall_risk_score", 0.0)
    tier = risk_summary.get("risk_tier", "Moderate")
    
    md_content = f"""# CLIMATE RISK INTELLIGENCE EXECUTIVE BRIEF
**Asset:** {fac_name}  
**Location:** {city}, {country} | **Sector:** {sector}  
**Asset Replacement Value:** ${asset_val:.1f} Million USD  
**Date of Assessment:** 2026-10-27 | **Framework:** IPCC AR6 & TCFD Physical Risk Guidelines  

---

## 1. Executive Climate Vulnerability Classification
- **Composite Climate Risk Score:** **{score:.1f} / 100**
- **Risk Classification Tier:** **{tier.upper()}**
- **Overall Hazard Intensity:** {risk_summary.get('composite_hazard', 0.0):.1f} / 100
- **Operational Vulnerability Factor:** {risk_summary.get('vulnerability_factor', 0.0):.2f}

### Hazard Exposure Spectrum
"""
    for haz, val in hazards_data.items():
        md_content += f"- **{haz}:** {val:.1f} / 100\n"

    md_content += f"""
---

## 2. Quantitative Financial & Operational Exposure
- **Total Climate Value-at-Risk (Annual VaR):** **${financial_data.get('total_climate_var_m', 0.0):.2f}M USD**
- **Direct Expected Physical Damage:** ${financial_data.get('expected_physical_loss_m', 0.0):.2f}M USD ({financial_data.get('damage_ratio_pct', 0.0):.2f}% of asset value)
- **Business Interruption Revenue-at-Risk:** ${financial_data.get('revenue_at_risk_m', 0.0):.2f}M USD
- **Estimated Annual Downtime:** **{financial_data.get('downtime_days', 0.0):.1f} Operating Days**
- **Labor Productivity Drag:** {financial_data.get('worker_productivity_loss_pct', 0.0):.1f}% (Est. Cost: ${financial_data.get('workforce_cost_m', 0.0):.2f}M USD)
- **Projected Insurance Premium Loading:** +{financial_data.get('insurance_surge_pct', 0.0):.1f}% surge (New Premium: ${financial_data.get('projected_insurance_m', 0.0):.2f}M/year)

---

## 3. Recommended Adaptation & Engineering Actions
"""
    for idx, act in enumerate(mitigation_actions, 1):
        md_content += f"**{idx}. {act.get('action', '')}**  \n"
        md_content += f"*Category:* {act.get('category', '')} | *CapEx Tier:* {act.get('capex', '')} | *Risk Reduction:* {act.get('reduction', '')}  \n"
        md_content += f"{act.get('description', '')}\n\n"

    md_content += """
---
## 4. TCFD / CSRD Disclosure Statement
*This assessment satisfies TCFD Strategy Recommendation b (Impact of climate risks on business, strategy, and financial planning) and CSRD ESRS E1 Climate Change physical risk screening criteria.*
"""
    return md_content


def generate_executive_pdf_report(
    facility_data: Dict[str, Any],
    hazards_data: Dict[str, float],
    risk_summary: Dict[str, Any],
    financial_data: Dict[str, Any]
) -> bytes:
    """
    Renders an official executive PDF briefing document.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header Banner
    pdf.set_fill_color(15, 76, 58)  # Primary dark green
    pdf.rect(0, 0, 210, 26, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, "CLIMATEIQ | CLIMATE RISK INTELLIGENCE BRIEF", ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, "Enterprise Physical Climate Vulnerability & Financial Exposure Report", ln=True, align='C')
    
    pdf.ln(12)
    pdf.set_text_color(26, 32, 44)
    
    # Asset Information
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, f"Facility: {facility_data.get('facility_name', 'Facility')}", ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, f"Location: {facility_data.get('city', '')}, {facility_data.get('country', '')} | Sector: {facility_data.get('sector', '')}", ln=True)
    pdf.cell(0, 6, f"Asset Replacement Value: ${facility_data.get('asset_value_m', 0.0):.1f}M USD | Headcount: {facility_data.get('employees', 0):,}", ln=True)
    
    pdf.ln(4)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    # Risk Classification Callout Box
    score = risk_summary.get('overall_risk_score', 0.0)
    tier = risk_summary.get('risk_tier', 'Moderate')
    
    pdf.set_fill_color(248, 251, 249)
    pdf.rect(10, pdf.get_y(), 190, 24, 'F')
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(95, 12, f" Overall Climate Risk Score: {score:.1f} / 100", ln=False)
    pdf.cell(95, 12, f"Risk Classification: {tier.upper()}", ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(190, 8, f" Composite Hazard: {risk_summary.get('composite_hazard', 0.0):.1f}/100 | Vulnerability Factor: {risk_summary.get('vulnerability_factor', 0.0):.2f}", ln=True)
    
    pdf.ln(6)
    
    # Hazard Breakdown Table
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "Primary Climate Hazards Analysis", ln=True)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(235, 243, 238)
    pdf.cell(120, 7, "Hazard Dimension", border=1, fill=True)
    pdf.cell(70, 7, "Severity Rating (0 - 100)", border=1, fill=True, ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    for haz, val in hazards_data.items():
        pdf.cell(120, 6, haz, border=1)
        pdf.cell(70, 6, f"{val:.1f} / 100", border=1, ln=True)
        
    pdf.ln(6)
    
    # Financial Impact Summary
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, "Estimated Financial Impact & Value-at-Risk", ln=True)
    
    tot_var = financial_data.get('total_climate_var_m', 0.0)
    phys_loss = financial_data.get('expected_physical_loss_m', 0.0)
    rev_loss = financial_data.get('revenue_at_risk_m', 0.0)
    downtime = financial_data.get('downtime_days', 0.0)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"* Total Climate Value-at-Risk (Annual VaR): ${tot_var:.2f}M USD", ln=True)
    pdf.cell(0, 6, f"* Expected Direct Asset Physical Damage: ${phys_loss:.2f}M USD", ln=True)
    pdf.cell(0, 6, f"* Business Interruption Revenue Loss: ${rev_loss:.2f}M USD", ln=True)
    pdf.cell(0, 6, f"* Projected Annual Operational Downtime: {downtime:.1f} Days", ln=True)
    pdf.cell(0, 6, f"* Insurance Premium Surcharge: +{financial_data.get('insurance_surge_pct', 0.0):.1f}%", ln=True)
    
    pdf.ln(8)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(113, 128, 150)
    pdf.cell(0, 5, "Generated automatically by ClimateIQ Analytics Platform. Complies with TCFD and IPCC AR6 metrics.", ln=True, align='C')
    
    return bytes(pdf.output())
