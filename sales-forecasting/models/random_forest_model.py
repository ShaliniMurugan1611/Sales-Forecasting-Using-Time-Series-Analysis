"""
Random Forest Forecast Model
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class RandomForestForecast:
    def __init__(self, n_estimators=100, random_state=12345):
        self.name = "Random Forest"
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = RandomForestRegressor(n_estimators=n_estimators, 
                                          random_state=random_state,
                                          n_jobs=-1)
        self.scaler = StandardScaler()
        self.fitted = False
        self.last_values = []
        self.feature_cols = []
    
    def create_features(self, series):
        """Create time-based features"""
        df_feat = pd.DataFrame({'sales': series.values})
        df_feat['lag1'] = df_feat['sales'].shift(1)
        df_feat['lag7'] = df_feat['sales'].shift(7)
        df_feat['lag14'] = df_feat['sales'].shift(14)
        df_feat['lag28'] = df_feat['sales'].shift(28)
        df_feat['rolling_mean7'] = df_feat['sales'].shift(1).rolling(window=7).mean()
        df_feat['rolling_mean14'] = df_feat['sales'].shift(1).rolling(window=14).mean()
        df_feat['rolling_std7'] = df_feat['sales'].shift(1).rolling(window=7).std()
        
        # Drop NaN rows
        df_feat = df_feat.dropna()
        return df_feat
    
    def fit(self, train_series):
        """Fit Random Forest model"""
        if len(train_series) < 40:
            raise ValueError("Insufficient data for Random Forest (need >= 40)")
        
        df_feat = self.create_features(train_series)
        if len(df_feat) == 0:
            raise ValueError("No valid features created")
        
        self.feature_cols = ['lag1', 'lag7', 'lag14', 'lag28', 
                            'rolling_mean7', 'rolling_mean14', 'rolling_std7']
        X = df_feat[self.feature_cols]
        y = df_feat['sales']
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.fitted = True
        
        # Store last values for recursive forecasting
        self.last_values = list(train_series.values[-28:])
        return self
    
    def predict_recursive(self, steps):
        """Generate multi-step forecasts recursively"""
        if not self.fitted:
            raise ValueError("Model must be fitted first")
        
        predictions = []
        history = list(self.last_values)
        
        for step in range(steps):
            if len(history) < 28:
                # Use available history
                hist_arr = np.array(history)
            else:
                hist_arr = np.array(history[-28:])
            
            # Create features from current history
            features = {}
            features['lag1'] = history[-1] if len(history) >= 1 else 0
            features['lag7'] = history[-7] if len(history) >= 7 else (history[0] if len(history) > 0 else 0)
            features['lag14'] = history[-14] if len(history) >= 14 else (history[0] if len(history) > 0 else 0)
            features['lag28'] = history[-28] if len(history) >= 28 else (history[0] if len(history) > 0 else 0)
            features['rolling_mean7'] = np.mean(history[-7:]) if len(history) >= 7 else np.mean(history)
            features['rolling_mean14'] = np.mean(history[-14:]) if len(history) >= 14 else np.mean(history)
            features['rolling_std7'] = np.std(history[-7:]) if len(history) >= 7 else 0
            
            X_pred = pd.DataFrame([features])[self.feature_cols]
            X_pred_scaled = self.scaler.transform(X_pred)
            pred = self.model.predict(X_pred_scaled)[0]
            pred = max(0, float(pred))
            predictions.append(pred)
            history.append(pred)
        
        return np.array(predictions)
    
    def forecast(self, train_series, steps):
        """Convenience method"""
        self.fit(train_series)
        return self.predict_recursive(steps)
