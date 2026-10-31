"""
Naive Forecast Model - uses last observed value
"""
import pandas as pd
import numpy as np

class NaiveForecast:
    def __init__(self):
        self.name = "Naive Forecast"
        self.last_value = None
        self.fitted = False
    
    def fit(self, train_series):
        """Fit naive model using last training value"""
        if len(train_series) == 0:
            raise ValueError("Training series is empty")
        self.last_value = float(train_series.iloc[-1])
        self.fitted = True
        return self
    
    def predict(self, steps):
        """Predict next steps using last value"""
        if not self.fitted:
            raise ValueError("Model must be fitted first")
        predictions = np.array([max(0, self.last_value)] * steps)
        return predictions
    
    def forecast(self, train_series, steps):
        """Convenience method"""
        self.fit(train_series)
        return self.predict(steps)
