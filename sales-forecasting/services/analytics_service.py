"""
Analytics service for generating insights and charts
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from services.data_service import DataService

class AnalyticsService:
    def __init__(self):
        self.data_service = DataService()
    
    def get_overview(self, df=None):
        """Get overview dashboard data"""
        if df is None:
            df = self.data_service.load_data()
        self.data_service.validate_dataframe(df)
        ts = self.data_service.preprocess(df)
        
        # KPIs
        total_revenue = float(df['sales'].sum())
        total_records = int(len(df))
        avg_daily_sales = float(ts['total_sales'].mean())
        
        # Best selling product
        product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=False)
        best_selling = product_sales.index[0] if len(product_sales) > 0 else "N/A"
        
        # Monthly trend
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy['month'] = df_copy['date'].dt.to_period('M')
        monthly = df_copy.groupby('month')['sales'].sum().reset_index()
        monthly['month_str'] = monthly['month'].astype(str)
        
        # Historical line chart
        hist_data = [{
            'date': row['date'].strftime('%Y-%m-%d'),
            'sales': float(row['total_sales'])
        } for _, row in ts.iterrows()]
        
        # Product-wise sales
        prod_data = [{'product': prod, 'sales': float(sales)} 
                    for prod, sales in product_sales.items()]
        
        # Monthly sales
        monthly_data = [{'month': row['month_str'], 'sales': float(row['sales'])} 
                       for _, row in monthly.iterrows()]
        
        return {
            'kpis': {
                'total_revenue': round(total_revenue, 2),
                'total_orders': total_records,
                'avg_daily_sales': round(avg_daily_sales, 2),
                'best_selling_product': best_selling,
                'predicted_future_revenue': 0,  # Will be updated by forecast
                'best_performing_model': 'N/A'
            },
            'historical_chart': hist_data,
            'product_chart': prod_data,
            'monthly_chart': monthly_data,
            'summary_stats': self.data_service.get_summary_stats(ts)
        }
    
    def get_analytics(self, df=None):
        """Get detailed analytics"""
        if df is None:
            df = self.data_service.load_data()
        self.data_service.validate_dataframe(df)
        ts = self.data_service.preprocess(df)
        
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy['month'] = df_copy['date'].dt.month
        df_copy['day_of_week'] = df_copy['date'].dt.day_name()
        df_copy['week'] = df_copy['date'].dt.isocalendar().week
        
        # Sales by day of week
        dow_sales = df_copy.groupby('day_of_week')['sales'].sum().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        dow_data = [{'day': day, 'sales': float(sales) if pd.notna(sales) else 0} 
                    for day, sales in dow_sales.items()]
        
        # Sales by category
        cat_sales = df_copy.groupby('category')['sales'].sum()
        cat_data = [{'category': cat, 'sales': float(sales)} 
                    for cat, sales in cat_sales.items()]
        
        # Sales by region
        reg_sales = df_copy.groupby('region')['sales'].sum()
        reg_data = [{'region': reg, 'sales': float(sales)} 
                    for reg, sales in reg_sales.items()]
        
        # Trend analysis
        if len(ts) > 30:
            recent_avg = ts.tail(30)['total_sales'].mean()
            early_avg = ts.head(30)['total_sales'].mean()
            trend = 'increasing' if recent_avg > early_avg * 1.05 else ('decreasing' if recent_avg < early_avg * 0.95 else 'stable')
        else:
            trend = 'insufficient data'
        
        # Highest sales month
        monthly = df_copy.groupby('month')['sales'].sum()
        highest_month = monthly.idxmax() if len(monthly) > 0 else None
        month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                       7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        
        insights = [
            f"Sales trend: {trend}",
            f"Highest sales month: {month_names.get(highest_month, 'N/A')}",
            f"Average daily revenue: ${ts['total_sales'].mean():.2f}",
            f"Total transactions: {len(df)}",
            f"Data covers {len(ts)} days"
        ]
        
        return {
            'day_of_week_chart': dow_data,
            'category_chart': cat_data,
            'region_chart': reg_data,
            'trend': trend,
            'insights': insights,
            'summary': self.data_service.get_summary_stats(ts)
        }
    
    def generate_business_insights(self, df=None, forecast_data=None):
        """Generate business insights from historical and forecast data"""
        if df is None:
            df = self.data_service.load_data()
        self.data_service.validate_dataframe(df)
        ts = self.data_service.preprocess(df)
        
        # Historical insights
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy['month'] = df_copy['date'].dt.month
        
        monthly = df_copy.groupby('month')['sales'].sum()
        highest_month_num = monthly.idxmax()
        month_names = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                       7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        highest_month = month_names.get(highest_month_num, 'N/A')
        
        product_sales = df_copy.groupby('product')['sales'].sum().sort_values(ascending=False)
        best_selling = product_sales.index[0] if len(product_sales) > 0 else "N/A"
        
        avg_daily = ts['total_sales'].mean()
        recent_avg = ts.tail(30)['total_sales'].mean() if len(ts) >= 30 else avg_daily
        
        if recent_avg > avg_daily * 1.05:
            trend_msg = "Sales are showing an increasing trend in recent periods."
        elif recent_avg < avg_daily * 0.95:
            trend_msg = "Sales are showing a decreasing trend in recent periods."
        else:
            trend_msg = "Sales are relatively stable with minor fluctuations."
        
        insights = [
            trend_msg,
            f"Highest-sales month in historical data: {highest_month}",
            f"Best-selling product: {best_selling}",
            f"Average daily revenue: ${avg_daily:.2f}",
        ]
        
        if forecast_data and isinstance(forecast_data, list):
            forecast_total = sum([f.get('predicted_sales', 0) for f in forecast_data])
            insights.append(f"Forecasted total revenue ({len(forecast_data)} days): ${forecast_total:.2f}")
            if recent_avg > 0:
                diff_pct = ((forecast_total / len(forecast_data)) - recent_avg) / recent_avg * 100
                if diff_pct > 5:
                    insights.append(f"Forecast suggests {diff_pct:.1f}% higher average daily sales compared to recent 30-day average.")
                elif diff_pct < -5:
                    insights.append(f"Forecast suggests {abs(diff_pct):.1f}% lower average daily sales compared to recent 30-day average.")
                else:
                    insights.append("Forecast suggests average daily sales similar to recent trends.")
        
        return insights
