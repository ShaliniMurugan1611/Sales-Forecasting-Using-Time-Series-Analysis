#!/usr/bin/env python3
"""
Generate realistic synthetic sales dataset for Sales Forecasting project
"""
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set seeds for reproducibility
random.seed(12345)
np.random.seed(12345)

def generate_sales_data(output_path=None):
    """Generate synthetic sales data"""
    if output_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        output_path = base_dir / "data" / "sales_data.csv"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Products and categories
    products = [
        ("Laptop Pro", "Electronics"),
        ("Smartphone X", "Electronics"),
        ("Wireless Headphones", "Electronics"),
        ("Desk Chair", "Furniture"),
        ("Office Desk", "Furniture"),
        ("Coffee Maker", "Appliances"),
        ("Blender", "Appliances"),
        ("Running Shoes", "Sports"),
        ("Yoga Mat", "Sports"),
        ("Backpack", "Accessories"),
    ]
    
    regions = ["North", "South", "East", "West", "Central"]
    
    # Generate 2 years of daily data (730 days)
    start_date = datetime(2024, 1, 1)
    end_date = start_date + timedelta(days=729)
    
    records = []
    
    for single_date in pd.date_range(start_date, end_date, freq='D'):
        # Add weekly pattern (higher sales on weekends)
        day_of_week = single_date.weekday()  # 0=Monday
        is_weekend = day_of_week >= 5
        
        # Add some seasonal pattern (slight increase in Dec)
        month = single_date.month
        seasonal_factor = 1.0
        if month == 12:
            seasonal_factor = 1.15
        elif month in [11, 1]:
            seasonal_factor = 1.08
        elif month in [6, 7]:
            seasonal_factor = 1.05
        
        # Generate 2-5 transactions per day
        num_transactions = random.randint(2, 5)
        
        for _ in range(num_transactions):
            product_name, category = random.choice(products)
            region = random.choice(regions)
            
            # Base quantity varies by product
            if category == "Electronics":
                base_qty = random.randint(1, 3)
                base_price = random.uniform(299.99, 1299.99)
            elif category == "Furniture":
                base_qty = random.randint(1, 2)
                base_price = random.uniform(149.99, 599.99)
            elif category == "Appliances":
                base_qty = random.randint(1, 4)
                base_price = random.uniform(29.99, 199.99)
            elif category == "Sports":
                base_qty = random.randint(1, 6)
                base_price = random.uniform(19.99, 149.99)
            else:  # Accessories
                base_qty = random.randint(2, 8)
                base_price = random.uniform(9.99, 79.99)
            
            # Apply factors
            quantity = max(1, int(base_qty * (1.2 if is_weekend else 1.0) * seasonal_factor * random.uniform(0.8, 1.2)))
            unit_price = round(base_price * random.uniform(0.95, 1.05), 2)
            discount = round(random.choice([0, 0, 0, 0.05, 0.10, 0.15]), 2)
            
            # Calculate sales
            sales = round(quantity * unit_price * (1 - discount), 2)
            
            records.append({
                'date': single_date.strftime('%Y-%m-%d'),
                'product': product_name,
                'category': category,
                'quantity': quantity,
                'unit_price': unit_price,
                'discount': discount,
                'sales': sales,
                'region': region
            })
    
    df = pd.DataFrame(records)
    df = df.sort_values(['date', 'product']).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} records in {output_path}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Products: {df['product'].nunique()}")
    print(f"Regions: {df['region'].nunique()}")
    
    return df

if __name__ == '__main__':
    generate_sales_data()
