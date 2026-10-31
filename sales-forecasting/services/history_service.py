"""
History service
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database.db import ForecastHistoryDB

class HistoryService:
    def __init__(self):
        self.db = ForecastHistoryDB()
    
    def save_forecast(self, *args, **kwargs):
        return self.db.save_forecast(*args, **kwargs)
    
    def get_history(self, limit=50):
        return self.db.get_history(limit)
    
    def get_forecast(self, run_id):
        return self.db.get_forecast_by_run_id(run_id)
