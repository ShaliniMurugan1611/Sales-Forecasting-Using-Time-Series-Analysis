"""
Tests for data processing
"""
import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from services.data_service import DataService

def test_data_service_load():
    ds = DataService()
    try:
        df = ds.load_data()
        assert df is not None
        assert len(df) > 0
    except FileNotFoundError:
        pytest.skip("Dataset not found")

def test_validate_dataframe():
    ds = DataService()
    df = pd.DataFrame({
        'date': ['2024-01-01'],
        'product': ['Test'],
        'category': ['Test'],
        'quantity': [1],
        'unit_price': [10],
        'discount': [0],
        'sales': [10],
        'region': ['North']
    })
    assert ds.validate_dataframe(df) == True

def test_preprocess():
    ds = DataService()
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-01', '2024-01-02'],
        'product': ['A', 'A', 'A'],
        'category': ['X', 'X', 'X'],
        'quantity': [1, 2, 1],
        'unit_price': [10, 10, 10],
        'discount': [0, 0, 0],
        'sales': [10, 20, 10],
        'region': ['North', 'North', 'North']
    })
    ts = ds.preprocess(df)
    assert len(ts) == 2  # 2 days
    assert ts['total_sales'].iloc[0] == 30  # aggregated
