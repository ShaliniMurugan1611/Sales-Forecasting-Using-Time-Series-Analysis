"""
Model evaluation module
"""
import numpy as np
import pandas as pd

class ModelEvaluator:
    def __init__(self):
        pass
    
    def mae(self, actual, predicted):
        """Mean Absolute Error"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        return float(np.mean(np.abs(actual - predicted)))
    
    def rmse(self, actual, predicted):
        """Root Mean Square Error"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))
    
    def mape(self, actual, predicted):
        """Mean Absolute Percentage Error (only for nonzero actual)"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        # Avoid division by zero
        mask = actual != 0
        if mask.sum() == 0:
            return float('nan')
        return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)
    
    def wape(self, actual, predicted):
        """Weighted Absolute Percentage Error"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        denominator = np.sum(np.abs(actual))
        if denominator == 0:
            return float('nan')
        return float(np.sum(np.abs(actual - predicted)) / denominator * 100)
    
    def r2(self, actual, predicted):
        """R-squared"""
        actual = np.array(actual)
        predicted = np.array(predicted)
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        if ss_tot == 0:
            return float('nan')
        return float(1 - (ss_res / ss_tot))
    
    def evaluate_all(self, actual, predicted):
        """Evaluate all metrics"""
        return {
            'mae': self.mae(actual, predicted),
            'rmse': self.rmse(actual, predicted),
            'mape': self.mape(actual, predicted),
            'wape': self.wape(actual, predicted),
            'r2': self.r2(actual, predicted)
        }
    
    def get_best_model(self, results, metric='mae'):
        """Get best model based on metric (lower is better for mae/rmse/mape/wape)"""
        valid_results = [(name, res) for name, res in results.items() 
                        if res.get('evaluation_status') == 'success' 
                        and res.get(metric) is not None 
                        and not (isinstance(res.get(metric), float) and np.isnan(res.get(metric)))]
        
        if not valid_results:
            return None
        
        if metric in ['mae', 'rmse', 'mape', 'wape']:
            best = min(valid_results, key=lambda x: x[1][metric])
        elif metric == 'r2':
            best = max(valid_results, key=lambda x: x[1][metric])
        else:
            best = min(valid_results, key=lambda x: x[1]['mae'])
        
        return best[0]
