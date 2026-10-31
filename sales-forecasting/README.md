# README.md - Sales Forecasting using Time-Series Analysis

## Project Overview

A complete, fully functional, industry-oriented AI/ML full-stack web application for sales forecasting using time-series analysis. This application analyzes historical sales data, trains multiple forecasting models, compares their performance, and predicts future sales through an interactive web dashboard.

## Features

- **Interactive Dashboard**: Professional business analytics dashboard with KPIs and charts
- **Multiple Forecasting Models**: Naive Forecast, ARIMA, Random Forest, Linear Regression
- **Model Comparison**: Compare all models on same test period with evaluation metrics
- **Data Management**: CSV upload with validation, synthetic dataset generation
- **Forecast History**: SQLite storage of all forecast runs
- **Export Functionality**: Download forecasts as CSV
- **Business Insights**: Automated data-driven insights generation
- **Responsive Design**: Bootstrap 5 responsive layout

## Technology Stack

### Frontend
- HTML5, CSS3, Vanilla JavaScript
- Bootstrap 5
- Chart.js

### Backend
- Python 3.8+
- Flask
- REST API

### Machine Learning
- pandas, numpy
- scikit-learn (Random Forest, Linear Regression)
- statsmodels (ARIMA)

### Database
- SQLite

## Prerequisites

- Windows OS
- Python 3.8 or higher
- Visual Studio Code
- Web browser (Chrome, Firefox, Edge)

## Installation and Setup

### 1. Open Project in VS Code
```bash
cd C:\Users\MONIKA
code sales-forecasting
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
```bash
.venv\Scripts\activate
```

### 4. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Generate Synthetic Dataset
```bash
python scripts\generate_dataset.py
```

### 6. Run the Application
```bash
python app.py
```

### 7. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Running Tests

```bash
python -m pytest -q
```

For verbose output:
```bash
python -m pytest -v
```

## Project Structure

```
sales-forecasting/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── data/                  # Dataset storage
├── scripts/               # Utility scripts
├── models/                # ML models
├── services/              # Business logic
├── database/              # Database layer
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── tests/                 # Test suite
└── instance/              # SQLite database
```

## Usage Guide

### Overview Dashboard
View KPIs, historical trends, product sales, and business insights.

### Sales Analytics
Analyze sales by day of week, category, and region.

### Forecasting
1. Select product, region, forecast horizon, and algorithm
2. Click "Generate Forecast"
3. View forecast chart, summary, and insights
4. Download forecast as CSV

### Model Comparison
Compare all four models on the same test period to identify best performer.

### Dataset Management
Upload your own CSV file or use the generated dataset.

### Forecast History
View all previous forecast runs and download them again.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/overview` - Dashboard overview data
- `GET /api/sales/history` - Historical sales data
- `GET /api/sales/products` - Available products and regions
- `GET /api/analytics` - Analytics data
- `POST /api/upload` - Upload CSV file
- `POST /api/forecast` - Generate forecast
- `POST /api/compare-models` - Compare all models
- `GET /api/forecast/history` - Forecast history
- `GET /api/forecast/download` - Download forecast CSV

## Troubleshooting

### Module Not Found Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change port in app.py or kill existing process.

### Dataset Not Found
```bash
python scripts\generate_dataset.py
```

### Statsmodels Issues
Ensure compatible versions are installed. The app handles ARIMA failures gracefully.

## Notes

- Forecasts are estimates, not guaranteed future sales
- All models use chronological train/test splitting (no data leakage)
- Missing dates are filled with 0 (clearly distinguished)
- Negative predictions are clamped to 0
- No API keys or cloud services required

## License

Educational Project - Sales Forecasting using Time-Series Analysis
