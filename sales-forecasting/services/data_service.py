"""
Data service for loading and preprocessing sales data
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import DEFAULT_DATASET

class DataService:
    def __init__(self):
        self.data = None
        self.df = None
    
    def load_data(self, file_path=None):
        """Load sales data from CSV"""
        if file_path is None:
            file_path = DEFAULT_DATASET
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        self.df = df
        return df
    
    def validate_dataframe(self, df):
        """Validate dataframe has required columns"""
        required_cols = ['date', 'product', 'category', 'quantity', 
                        'unit_price', 'discount', 'sales', 'region']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True
    
    def preprocess(self, df=None, product_filter=None, region_filter=None):
        """Preprocess data for forecasting"""
        if df is None:
            df = self.df
        if df is None:
            raise ValueError("No data loaded")
        
        df = df.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Apply filters
        if product_filter and product_filter != 'all':
            df = df[df['product'] == product_filter]
        if region_filter and region_filter != 'all':
            df = df[df['region'] == region_filter]
        
        # Sort by date
        df = df.sort_values('date')
        
        # Aggregate by date
        daily_sales = df.groupby('date').agg({
            'sales': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        daily_sales = daily_sales.rename(columns={'sales': 'total_sales', 'quantity': 'total_quantity'})
        
        # Create regular daily time series
        date_range = pd.date_range(start=daily_sales['date'].min(), 
                                   end=daily_sales['date'].max(), 
                                   freq='D')
        ts = pd.DataFrame({'date': date_range})
        ts = ts.merge(daily_sales, on='date', how='left')
        
        # Document missing date strategy - fill with 0 (clear distinction from missing)
        ts['total_sales'] = ts['total_sales'].fillna(0)
        ts['total_quantity'] = ts['total_quantity'].fillna(0)
        
        ts = ts.sort_values('date').reset_index(drop=True)
        
        return ts
    
    def get_products(self, df=None):
        """Get list of unique products"""
        if df is None:
            df = self.df
        if df is None:
            return []
        return sorted(df['product'].unique().tolist())
    
    def get_regions(self, df=None):
        """Get list of unique regions"""
        if df is None:
            df = self.df
        if df is None:
            return []
        return sorted(df['region'].unique().tolist())
    
    def get_summary_stats(self, ts):
        """Get summary statistics"""
        return {
            'total_sales': float(ts['total_sales'].sum()),
            'avg_daily_sales': float(ts['total_sales'].mean()),
            'max_daily_sales': float(ts['total_sales'].max()),
            'min_daily_sales': float(ts['total_sales'].min()),
            'num_days': int(len(ts)),
            'start_date': ts['date'].min().strftime('%Y-%m-%d'),
            'end_date': ts['date'].max().strftime('%Y-%m-%d')
        }
