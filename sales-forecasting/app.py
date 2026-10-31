"""
Flask application for Sales Forecasting
"""
import os
import json
import csv
from io import StringIO
from datetime import datetime
from pathlib import Path
import sys

from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename

sys.path.append(str(Path(__file__).parent))

from config import (
    BASE_DIR, DATA_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES,
    DEFAULT_DATASET, ALLOWED_HORIZONS, ensure_directories
)
from services.data_service import DataService
from services.analytics_service import AnalyticsService
from services.forecasting_service import ForecastingService
from services.history_service import HistoryService

app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_BYTES

# Initialize services
ensure_directories()
data_service = DataService()
analytics_service = AnalyticsService()
forecasting_service = ForecastingService()
history_service = HistoryService()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sales Forecasting API'
    })

@app.route('/api/overview')
def overview():
    try:
        df = data_service.load_data()
        result = analytics_service.get_overview(df)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sales/history')
def sales_history():
    try:
        df = data_service.load_data()
        data_service.validate_dataframe(df)
        ts = data_service.preprocess(df)
        history = [{'date': row['date'].strftime('%Y-%m-%d'), 
                    'sales': float(row['total_sales']),
                    'quantity': float(row['total_quantity'])} 
                   for _, row in ts.iterrows()]
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sales/products')
def sales_products():
    try:
        df = data_service.load_data()
        products = data_service.get_products(df)
        regions = data_service.get_regions(df)
        return jsonify({'success': True, 'products': ['all'] + products, 'regions': ['all'] + regions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics')
def analytics():
    try:
        df = data_service.load_data()
        result = analytics_service.get_analytics(df)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'}), 400
        
        filename = secure_filename(file.filename)
        # Validate file content
        content = file.read()
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            return jsonify({'success': False, 'error': 'File too large'}), 400
        
        # Try to parse CSV
        try:
            df = pd.read_csv(StringIO(content.decode('utf-8')))
        except Exception as e:
            return jsonify({'success': False, 'error': f'Invalid CSV: {str(e)}'}), 400
        
        # Validate
        data_service.validate_dataframe(df)
        
        # Save uploaded file
        upload_path = DATA_DIR / f'uploaded_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
        with open(upload_path, 'wb') as f:
            f.write(content)
        
        return jsonify({
            'success': True, 
            'message': 'File uploaded successfully',
            'filename': filename,
            'rows': len(df)
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forecast', methods=['POST'])
def forecast():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        model_name = data.get('model', 'naive')
        horizon = int(data.get('horizon', 30))
        product_filter = data.get('product', 'all')
        region_filter = data.get('region', 'all')
        
        if horizon not in ALLOWED_HORIZONS:
            return jsonify({'success': False, 'error': f'Horizon must be one of {ALLOWED_HORIZONS}'}), 400
        
        df = data_service.load_data()
        data_service.validate_dataframe(df)
        ts = data_service.preprocess(df, product_filter, region_filter)
        
        result = forecasting_service.forecast_single_model(
            model_name, ts, horizon, product_filter, region_filter
        )
        
        if result.get('success'):
            # Save to history
            try:
                history_service.save_forecast(
                    result['run_id'],
                    result['model_name'],
                    result['forecast_horizon'],
                    result['forecast_results'],
                    result.get('evaluation_metrics'),
                    'default',
                    product_filter,
                    region_filter
                )
            except:
                pass  # Don't fail if history save fails
            
            # Generate insights
            insights = analytics_service.generate_business_insights(df, result['forecast_results'])
            result['insights'] = insights
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare-models', methods=['POST'])
def compare_models():
    try:
        data = request.get_json() or {}
        product_filter = data.get('product', 'all')
        region_filter = data.get('region', 'all')
        horizon = int(data.get('horizon', 30))
        
        df = data_service.load_data()
        data_service.validate_dataframe(df)
        ts = data_service.preprocess(df, product_filter, region_filter)
        
        result = forecasting_service.compare_all_models(ts, horizon)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forecast/history')
def forecast_history():
    try:
        history = history_service.get_history()
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/forecast/download')
def download_forecast():
    try:
        run_id = request.args.get('run_id')
        if run_id:
            forecast_data = history_service.get_forecast(run_id)
            if not forecast_data:
                return jsonify({'success': False, 'error': 'Forecast not found'}), 404
            results = forecast_data['forecast_results']
        else:
            # Get latest from request or return empty
            results = []
        
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['forecast_date', 'predicted_sales', 'model'])
        for row in results:
            cw.writerow([row.get('forecast_date'), row.get('predicted_sales'), 
                        forecast_data.get('model_name') if run_id else 'N/A'])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure everything is initialized
    ensure_directories()
    try:
        # Generate dataset if missing
        if not DEFAULT_DATASET.exists():
            from scripts.generate_dataset import generate_sales_data
            generate_sales_data()
    except:
        pass
    
    try:
        # Initialize database
        history_service = HistoryService()
    except:
        pass
    
    app.run(debug=True, host='127.0.0.1', port=5000)
