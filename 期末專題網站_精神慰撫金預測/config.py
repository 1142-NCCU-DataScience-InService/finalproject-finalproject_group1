"""
全域路徑與設定（使用相對路徑，可在任何電腦執行）。
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

DATASET_CSV = DATA_DIR / "dataset_cleaned.csv"
MODEL_PATH = MODEL_DIR / "rf_model.pkl"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# 模型相關常數
INJURY_MAPPING = {"傷害": 1, "重傷": 2, "死亡": 3}
INJURY_REVERSE = {v: k for k, v in INJURY_MAPPING.items()}

# 模型平均誤差（來自 README 報告）
MODEL_MAE = 304969
DATASET_SIZE = 7050
