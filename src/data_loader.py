"""
Data loading and dataset generation module for ClimateIQ.
Provides cached access to global locations, enterprise facilities, and historical hazard records.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"

# ==============================================================================
# SEED DATA DEFINITIONS FOR BENCHMARK CORPORATE PORTFOLIO & LOCATIONS
# ==============================================================================
LOCATIONS_SEED = [
    # City, Country, Lat, Lon, Elevation, DistCoast, Flood, Heat, Drought, Wildfire, Rain, Zone
    ("Mumbai", "India", 19.0760, 72.8777, 14, 2, 88.0, 78.5, 32.0, 18.0, 94.0, "Tropical"),
    ("New York", "USA", 40.7128, -74.0060, 10, 5, 76.0, 62.0, 28.0, 15.0, 72.0, "Temperate"),
    ("Singapore", "Singapore", 1.3521, 103.8198, 15, 1, 65.0, 85.0, 15.0, 12.0, 84.0, "Tropical"),
    ("Rotterdam", "Netherlands", 51.9244, 4.4777, -2, 25, 82.0, 42.0, 30.0, 10.0, 68.0, "Temperate"),
    ("Tokyo", "Japan", 35.6762, 139.6503, 40, 6, 74.0, 71.0, 22.0, 20.0, 80.0, "Temperate"),
    ("Houston", "USA", 29.7604, -95.3698, 15, 60, 92.0, 86.0, 48.0, 35.0, 90.0, "Subtropical"),
    ("Dubai", "UAE", 25.2048, 55.2708, 5, 2, 35.0, 96.0, 88.0, 12.0, 30.0, "Arid"),
    ("Frankfurt", "Germany", 50.1109, 8.6821, 112, 350, 45.0, 58.0, 52.0, 38.0, 54.0, "Temperate"),
    ("Sydney", "Australia", -33.8688, 151.2093, 19, 4, 58.0, 76.0, 68.0, 84.0, 64.0, "Temperate"),
    ("São Paulo", "Brazil", -23.5505, -46.6333, 760, 55, 68.0, 64.0, 74.0, 40.0, 78.0, "Subtropical"),
    ("Jakarta", "Indonesia", -6.2088, 106.8456, 8, 1, 95.0, 82.0, 25.0, 15.0, 92.0, "Tropical"),
    ("London", "UK", 51.5074, -0.1278, 25, 65, 56.0, 54.0, 46.0, 18.0, 58.0, "Temperate"),
    ("Cairo", "Egypt", 30.0444, 31.2357, 23, 160, 28.0, 92.0, 90.0, 22.0, 18.0, "Arid"),
    ("Shanghai", "China", 31.2304, 121.4737, 4, 30, 86.0, 75.0, 38.0, 16.0, 82.0, "Subtropical"),
    ("Los Angeles", "USA", 34.0522, -118.2437, 89, 18, 38.0, 80.0, 82.0, 88.0, 44.0, "Mediterranean"),
    ("Bangkok", "Thailand", 13.7563, 100.5018, 2, 25, 91.0, 86.0, 30.0, 14.0, 89.0, "Tropical"),
    ("Seoul", "South Korea", 37.5665, 126.9780, 38, 30, 64.0, 68.0, 35.0, 26.0, 78.0, "Continental"),
    ("Phoenix", "USA", 33.4484, -112.0740, 331, 380, 20.0, 98.0, 94.0, 55.0, 22.0, "Arid"),
    ("Chennai", "India", 13.0827, 80.2707, 6, 1, 90.0, 84.0, 62.0, 15.0, 88.0, "Tropical"),
    ("Vancouver", "Canada", 49.2827, -123.1207, 4, 1, 52.0, 48.0, 35.0, 65.0, 82.0, "Temperate"),
    ("Valencia", "Spain", 39.4699, -0.3763, 15, 3, 75.0, 79.0, 76.0, 60.0, 84.0, "Mediterranean"),
    ("Johannesburg", "South Africa", -26.2041, 28.0473, 1753, 480, 30.0, 62.0, 78.0, 50.0, 48.0, "Subtropical"),
    ("Ho Chi Minh City", "Vietnam", 10.8231, 106.6297, 19, 45, 89.0, 84.0, 28.0, 15.0, 91.0, "Tropical"),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816, 25, 5, 68.0, 66.0, 44.0, 22.0, 70.0, "Subtropical"),
    ("Melbourne", "Australia", -37.8136, 144.9631, 31, 8, 48.0, 72.0, 65.0, 80.0, 52.0, "Temperate"),
]

FACILITIES_SEED = [
    # ID, Name, Sector, City, Country, AssetVal($M), Rev($M), Employees, BackupPower, FloodBarrier, WaterRecycle, InsurTier
    ("FAC-001", "GigaWatt Data Center Alpha", "Data Centers & IT Infrastructure", "Frankfurt", "Germany", 420.0, 185.0, 160, True, True, True, "Standard"),
    ("FAC-002", "Bayside Automated Port Hub", "Logistics, Ports & Warehousing", "Rotterdam", "Netherlands", 650.0, 310.0, 850, True, True, False, "Premium"),
    ("FAC-003", "Apex Microchip Fabrication 1", "Manufacturing & Heavy Industrial", "Phoenix", "USA", 850.0, 420.0, 1200, True, False, True, "Premium"),
    ("FAC-004", "Monsoon Coast Chemical Plant", "Manufacturing & Heavy Industrial", "Mumbai", "India", 380.0, 190.0, 720, False, False, False, "High Deductible"),
    ("FAC-005", "Equatorial Cloud Supercenter", "Data Centers & IT Infrastructure", "Singapore", "Singapore", 510.0, 240.0, 210, True, True, True, "Standard"),
    ("FAC-006", "Gulf Coast Petrochemicals", "Manufacturing & Heavy Industrial", "Houston", "USA", 720.0, 560.0, 940, True, False, False, "High Deductible"),
    ("FAC-007", "Solara Mega Solar Array", "Renewable Energy & Utilities", "Dubai", "UAE", 310.0, 95.0, 90, True, False, True, "Standard"),
    ("FAC-008", "Chao Phraya Electronics Assembly", "Manufacturing & Heavy Industrial", "Bangkok", "Thailand", 260.0, 140.0, 1800, False, False, False, "High Deductible"),
    ("FAC-009", "Hudson Financial Headquarters", "Commercial Real Estate & Hospitality", "New York", "USA", 940.0, 620.0, 3400, True, True, False, "Standard"),
    ("FAC-010", "Pacific Gateway Freight Terminal", "Logistics, Ports & Warehousing", "Tokyo", "Japan", 490.0, 275.0, 640, True, True, False, "Premium"),
    ("FAC-011", "Southern Grain Silos & Mills", "Agriculture & Food Supply", "Buenos Aires", "Argentina", 140.0, 85.0, 320, False, False, False, "Standard"),
    ("FAC-012", "Delta Agri Processing Center", "Agriculture & Food Supply", "Ho Chi Minh City", "Vietnam", 185.0, 110.0, 650, False, False, False, "High Deductible"),
    ("FAC-013", "Silicon Beach R&D Campus", "Data Centers & IT Infrastructure", "Los Angeles", "USA", 390.0, 215.0, 1100, True, False, True, "Standard"),
    ("FAC-014", "Coromandel Auto Components", "Manufacturing & Heavy Industrial", "Chennai", "India", 230.0, 130.0, 980, False, True, False, "Standard"),
    ("FAC-015", "Cascadia Pulp & Timber Logistics", "Logistics, Ports & Warehousing", "Vancouver", "Canada", 175.0, 92.0, 410, True, False, False, "Standard"),
    ("FAC-016", "Iberian Mediterranean Logistics Depot", "Logistics, Ports & Warehousing", "Valencia", "Spain", 210.0, 115.0, 380, True, False, False, "Standard"),
    ("FAC-017", "Highveld Industrial Refinery", "Manufacturing & Heavy Industrial", "Johannesburg", "South Africa", 290.0, 160.0, 520, False, False, True, "High Deductible"),
    ("FAC-018", "Thames Executive Trade Tower", "Commercial Real Estate & Hospitality", "London", "UK", 680.0, 340.0, 2200, True, True, False, "Standard"),
    ("FAC-019", "Yangtze Advanced Biotech Hub", "Manufacturing & Heavy Industrial", "Shanghai", "China", 450.0, 280.0, 1450, True, True, True, "Premium"),
    ("FAC-020", "Outback Lithium Extraction & Refining", "Renewable Energy & Utilities", "Sydney", "Australia", 540.0, 310.0, 460, True, False, True, "Standard"),
    ("FAC-021", "Nile Valley Agro Irrigation Base", "Agriculture & Food Supply", "Cairo", "Egypt", 120.0, 60.0, 280, False, False, True, "High Deductible"),
    ("FAC-022", "Paulista Financial & Tech Center", "Commercial Real Estate & Hospitality", "São Paulo", "Brazil", 360.0, 195.0, 1850, True, False, False, "Standard"),
    ("FAC-023", "Java Sea Multimodal Depot", "Logistics, Ports & Warehousing", "Jakarta", "Indonesia", 310.0, 145.0, 590, False, False, False, "High Deductible"),
    ("FAC-024", "Han River High-Tech Foundry", "Manufacturing & Heavy Industrial", "Seoul", "South Korea", 620.0, 390.0, 1300, True, True, True, "Premium"),
    ("FAC-025", "Victoria Clean Energy Substation", "Renewable Energy & Utilities", "Melbourne", "Australia", 280.0, 125.0, 110, True, False, False, "Standard"),
]


def ensure_datasets_exist() -> None:
    """Generate and write CSV datasets to data directory if not already created."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    loc_file = DATA_DIR / "global_locations.csv"
    fac_file = DATA_DIR / "business_facilities.csv"
    hist_file = DATA_DIR / "historical_hazards.csv"
    
    # 1. Locations CSV
    if not loc_file.exists():
        loc_cols = [
            "city", "country", "latitude", "longitude", "elevation_m",
            "distance_to_coast_km", "flood_hazard", "heat_hazard",
            "drought_hazard", "wildfire_hazard", "rainfall_hazard", "climate_zone"
        ]
        df_loc = pd.DataFrame(LOCATIONS_SEED, columns=loc_cols)
        df_loc.to_csv(loc_file, index=False)
    
    # 2. Facilities CSV
    if not fac_file.exists():
        fac_cols = [
            "facility_id", "facility_name", "sector", "city", "country",
            "asset_value_m", "annual_revenue_m", "employees",
            "backup_power", "flood_barrier", "water_recycling", "insurance_tier"
        ]
        df_fac = pd.DataFrame(FACILITIES_SEED, columns=fac_cols)
        df_fac.to_csv(fac_file, index=False)
        
    # 3. Historical Hazards Synthetic Benchmark CSV (2000-2024 records for ML and trend analytics)
    if not hist_file.exists():
        np.random.seed(42)
        records = []
        hazards = ["Flood", "Heatwave", "Drought", "Wildfire", "Severe Storm"]
        cities = [row[0] for row in LOCATIONS_SEED]
        
        for i in range(1, 451):
            year = np.random.randint(2004, 2025)
            month = np.random.randint(1, 13)
            city = np.random.choice(cities)
            hazard_type = np.random.choice(hazards)
            severity = np.clip(np.random.normal(55, 20), 10, 100)
            direct_economic_loss_m = np.round(severity * np.random.uniform(0.5, 3.2), 2)
            downtime_days = int(np.clip(severity * np.random.uniform(0.1, 0.45), 1, 45))
            disrupted_supply_chain = np.random.choice([0, 1], p=[0.35, 0.65])
            records.append({
                "record_id": f"HAZ-{i:04d}",
                "year": year,
                "month": month,
                "city": city,
                "hazard_type": hazard_type,
                "severity_index": round(severity, 1),
                "direct_loss_usd_m": direct_economic_loss_m,
                "facility_downtime_days": downtime_days,
                "supply_chain_disrupted": disrupted_supply_chain
            })
            
        df_hist = pd.DataFrame(records)
        df_hist.to_csv(hist_file, index=False)


@st.cache_data(ttl=3600)
def load_locations_data() -> pd.DataFrame:
    """Load global locations reference data."""
    ensure_datasets_exist()
    return pd.read_csv(DATA_DIR / "global_locations.csv")


@st.cache_data(ttl=3600)
def load_facilities_data() -> pd.DataFrame:
    """Load enterprise facility portfolio data merged with city hazard baseline."""
    ensure_datasets_exist()
    df_fac = pd.read_csv(DATA_DIR / "business_facilities.csv")
    df_loc = pd.read_csv(DATA_DIR / "global_locations.csv")
    
    # Merge facilities with location coordinates and baseline hazard metrics
    merged = pd.merge(df_fac, df_loc, on=["city", "country"], how="left")
    return merged


@st.cache_data(ttl=3600)
def load_historical_hazards() -> pd.DataFrame:
    """Load historical hazard benchmark occurrences."""
    ensure_datasets_exist()
    return pd.read_csv(DATA_DIR / "historical_hazards.csv")
