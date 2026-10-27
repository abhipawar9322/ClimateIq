"""
Unit tests for data loading and dataset generation.
"""

import pytest
import pandas as pd
from src.data_loader import (
    ensure_datasets_exist,
    load_locations_data,
    load_facilities_data,
    load_historical_hazards
)


def test_datasets_exist_and_load():
    ensure_datasets_exist()
    
    df_loc = load_locations_data()
    assert isinstance(df_loc, pd.DataFrame)
    assert len(df_loc) >= 20
    assert "city" in df_loc.columns
    assert "flood_hazard" in df_loc.columns
    
    df_fac = load_facilities_data()
    assert isinstance(df_fac, pd.DataFrame)
    assert len(df_fac) >= 20
    assert "facility_name" in df_fac.columns
    assert "asset_value_m" in df_fac.columns
    assert "latitude" in df_fac.columns  # Checked after merge
    
    df_hist = load_historical_hazards()
    assert isinstance(df_hist, pd.DataFrame)
    assert len(df_hist) >= 100
    assert "hazard_type" in df_hist.columns
