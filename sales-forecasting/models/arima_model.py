"""
ARIMA Forecast Model
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except Exception:
    STATSMODELS_AVAILABLE = False

class ARIMAForecast:
    def __init__(self, order=(1,1,1)):
        self.name = "ARIMA"
        self.order = order
        self.model = None
        self.model_fit = None
        self.fitted = False
    
    def fit(self, train_series):
        """Fit ARIMA model"""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")
        if len(train_series) < 10:
            raise ValueError("Insufficient data for ARIMA")
        
        try:
            series = pd.Series(train_series.values)
            self.model = ARIMA(series, order=self.order)
            self.model_fit = self.model.fit()
            self.fitted = True
            return self
        except Exception as e:
            # Try simpler order
            try:
                series = pd.Series(train_series.values)
                self.model = ARIMA(series, order=(1,0,1))
                self.model_fit = self.model.fit()
                self.fitted = True
                return self
            except Exception as e2:
                raise Exception(f"ARIMA fitting failed: {str(e2)}")
    
    def predict(self, steps):
        """Predict future steps"""
        if not self.fitted or self.model_fit is None:
            raise ValueError("Model must be fitted first")
        try:
            forecast = self.model_fit.forecast(steps=steps)
            predictions = np.array([max(0, float(x)) for x in forecast])
            return predictions
        except Exception as e:
            raise Exception(f"ARIMA prediction failed: {str(e)}")
    
    def forecast(self, train_series, steps):
        """Convenience method"""
        self.fit(train_series)
        return self.predict(steps)
