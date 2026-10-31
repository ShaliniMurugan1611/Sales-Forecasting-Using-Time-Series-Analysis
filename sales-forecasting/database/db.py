"""
Database module for forecast history
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import DATABASE_PATH, INSTANCE_DIR

class ForecastHistoryDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DATABASE_PATH
        self.db_path = Path(db_path)
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                model_name TEXT NOT NULL,
                forecast_horizon INTEGER NOT NULL,
                dataset_id TEXT,
                evaluation_metrics TEXT,
                forecast_results TEXT,
                product_filter TEXT,
                region_filter TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_forecast(self, run_id, model_name, forecast_horizon, 
                     forecast_results, evaluation_metrics=None,
                     dataset_id=None, product_filter=None, region_filter=None):
        """Save forecast run to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO forecast_history 
                (run_id, created_at, model_name, forecast_horizon, dataset_id,
                 evaluation_metrics, forecast_results, product_filter, region_filter)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                datetime.now().isoformat(),
                model_name,
                forecast_horizon,
                dataset_id or 'default',
                json.dumps(evaluation_metrics) if evaluation_metrics else None,
                json.dumps(forecast_results),
                product_filter,
                region_filter
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving forecast: {e}")
            return False
        finally:
            conn.close()
    
    def get_history(self, limit=50):
        """Get forecast history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM forecast_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    'id': row['id'],
                    'run_id': row['run_id'],
                    'created_at': row['created_at'],
                    'model_name': row['model_name'],
                    'forecast_horizon': row['forecast_horizon'],
                    'dataset_id': row['dataset_id'],
                    'evaluation_metrics': json.loads(row['evaluation_metrics']) if row['evaluation_metrics'] else None,
                    'forecast_results': json.loads(row['forecast_results']) if row['forecast_results'] else [],
                    'product_filter': row['product_filter'],
                    'region_filter': row['region_filter']
                })
            return history
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
        finally:
            conn.close()
    
    def get_forecast_by_run_id(self, run_id):
        """Get specific forecast by run_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM forecast_history WHERE run_id = ?', (run_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'run_id': row['run_id'],
                    'created_at': row['created_at'],
                    'model_name': row['model_name'],
                    'forecast_horizon': row['forecast_horizon'],
                    'dataset_id': row['dataset_id'],
                    'evaluation_metrics': json.loads(row['evaluation_metrics']) if row['evaluation_metrics'] else None,
                    'forecast_results': json.loads(row['forecast_results']) if row['forecast_results'] else [],
                    'product_filter': row['product_filter'],
                    'region_filter': row['region_filter']
                }
            return None
        except Exception as e:
            print(f"Error getting forecast: {e}")
            return None
        finally:
            conn.close()
