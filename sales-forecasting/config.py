# Configuration for Sales Forecasting App
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "forecast_history.db"
DEFAULT_DATASET = DATA_DIR / "sales_data.csv"

# Allowed upload settings
ALLOWED_EXTENSIONS = {"csv"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# Forecast settings
DEFAULT_FORECAST_HORIZON = 30
ALLOWED_HORIZONS = [7, 14, 30, 90]
RANDOM_SEED = 12345

# Model settings
TEST_SIZE_RATIO = 0.2  # use last 20% as test set (time series)
MIN_TRAIN_OBS = 30

def ensure_directories():
    """Ensure required directories exist"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "static" / "images").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "templates").mkdir(parents=True, exist_ok=True)
