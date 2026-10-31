"""
Tests for forecasting models
"""
import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from models.naive_model import NaiveForecast
from models.evaluation import ModelEvaluator

def test_naive_forecast():
    model = NaiveForecast()
    train = np.array([10, 12, 11, 13, 12])
    preds = model.forecast(train, 3)
    assert len(preds) == 3
    assert all(p >= 0 for p in preds)

def test_evaluation_metrics():
    evaluator = ModelEvaluator()
    actual = np.array([10, 12, 11, 13])
    pred = np.array([11, 11, 12, 12])
    mae = evaluator.mae(actual, pred)
    rmse = evaluator.rmse(actual, pred)
    assert mae >= 0
    assert rmse >= 0
    assert mae == 1.0
    assert rmse == 1.0

def test_chronological_split():
    from services.forecasting_service import ForecastingService
    import pandas as pd
    fs = ForecastingService()
    dates = pd.date_range('2024-01-01', periods=100)
    ts = pd.DataFrame({'date': dates, 'total_sales': np.random.rand(100)*100})
    train, test = fs.train_test_split_ts(ts, 0.2)
    assert len(train) == 80
    assert len(test) == 20
    assert train['date'].max() < test['date'].min() or train['date'].max() == test['date'].max()  # chronological
