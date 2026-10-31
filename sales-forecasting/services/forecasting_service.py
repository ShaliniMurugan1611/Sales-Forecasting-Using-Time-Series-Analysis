"""
Forecasting service to orchestrate models
"""
import pandas as pd
import numpy as np
from datetime import timedelta
import uuid
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from services.data_service import DataService
from models.naive_model import NaiveForecast
from models.arima_model import ARIMAForecast
from models.random_forest_model import RandomForestForecast
from models.linear_regression_model import LinearRegressionForecast
from models.evaluation import ModelEvaluator
from config import TEST_SIZE_RATIO, MIN_TRAIN_OBS

class ForecastingService:
    def __init__(self):
        self.data_service = DataService()
        self.evaluator = ModelEvaluator()
        self.models = {
            'naive': NaiveForecast,
            'arima': ARIMAForecast,
            'random_forest': RandomForestForecast,
            'linear_regression': LinearRegressionForecast
        }
    
    def train_test_split_ts(self, ts, test_ratio=TEST_SIZE_RATIO):
        """Chronological train/test split for time series"""
        n = len(ts)
        if n < MIN_TRAIN_OBS:
            raise ValueError(f"Insufficient data for forecasting (need >= {MIN_TRAIN_OBS} observations)")
        test_size = int(n * test_ratio)
        train_size = n - test_size
        train = ts.iloc[:train_size].copy()
        test = ts.iloc[train_size:].copy()
        return train, test
    
    def forecast_single_model(self, model_name, ts, horizon=30, product_filter=None, region_filter=None):
        """Generate forecast using a single model"""
        try:
            train, test = self.train_test_split_ts(ts)
            train_series = train['total_sales']
            test_series = test['total_sales']
            
            model_class = self.models.get(model_name)
            if not model_class:
                raise ValueError(f"Unknown model: {model_name}")
            
            model = model_class()
            predictions = model.forecast(train_series, horizon)
            
            # Evaluate on test set if possible
            eval_metrics = None
            try:
                # For evaluation, forecast on test period length
                test_pred = model.forecast(train_series, len(test_series))
                eval_metrics = self.evaluator.evaluate_all(test_series.values, test_pred)
            except Exception as e:
                eval_metrics = {'error': str(e)}
            
            # Generate future dates
            last_date = ts['date'].max()
            future_dates = [last_date + timedelta(days=i+1) for i in range(horizon)]
            
            forecast_results = []
            for i, (date, pred) in enumerate(zip(future_dates, predictions)):
                forecast_results.append({
                    'forecast_date': date.strftime('%Y-%m-%d'),
                    'predicted_sales': round(float(max(0, pred)), 2),
                    'day_index': i + 1
                })
            
            run_id = str(uuid.uuid4())
            
            return {
                'success': True,
                'run_id': run_id,
                'model_name': model.name,
                'model_key': model_name,
                'forecast_horizon': horizon,
                'forecast_results': forecast_results,
                'evaluation_metrics': eval_metrics,
                'training_status': 'success',
                'evaluation_status': 'success' if eval_metrics and 'error' not in eval_metrics else 'partial',
                'product_filter': product_filter,
                'region_filter': region_filter
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_name': model_name,
                'training_status': 'failed',
                'evaluation_status': 'failed'
            }
    
    def compare_all_models(self, ts, horizon=30):
        """Compare all models on same test period"""
        results = {}
        model_keys = ['naive', 'arima', 'random_forest', 'linear_regression']
        
        for model_key in model_keys:
            try:
                train, test = self.train_test_split_ts(ts)
                train_series = train['total_sales']
                test_series = test['total_sales']
                
                model_class = self.models.get(model_key)
                if not model_class:
                    results[model_key] = {'error': 'Model not found', 'evaluation_status': 'failed'}
                    continue
                
                model = model_class()
                test_pred = model.forecast(train_series, len(test_series))
                eval_metrics = self.evaluator.evaluate_all(test_series.values, test_pred)
                
                results[model_key] = {
                    'model_name': model.name,
                    'mae': eval_metrics['mae'],
                    'rmse': eval_metrics['rmse'],
                    'mape': eval_metrics['mape'],
                    'wape': eval_metrics['wape'],
                    'r2': eval_metrics['r2'],
                    'training_status': 'success',
                    'evaluation_status': 'success'
                }
            except Exception as e:
                results[model_key] = {
                    'model_name': model_key.replace('_', ' ').title(),
                    'error': str(e),
                    'training_status': 'failed',
                    'evaluation_status': 'failed'
                }
        
        # Find best model
        best_model = self.evaluator.get_best_model(results, metric='mae')
        
        return {
            'success': True,
            'comparison': results,
            'best_model': best_model,
            'test_period': {
                'start': test['date'].min().strftime('%Y-%m-%d'),
                'end': test['date'].max().strftime('%Y-%m-%d'),
                'days': len(test)
            } if 'test' in locals() else None
        }
