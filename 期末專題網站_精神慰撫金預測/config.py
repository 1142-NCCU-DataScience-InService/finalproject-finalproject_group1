"""
全域路徑與設定。

⚠️ 與專案 root 共用資源 — 不要在本資料夾再放一份 dataset / model / requirements。
路徑統一指向專案根目錄底下的 `data/processed/dataset_cleaned.csv` 與
`models/rf_model.pkl`，與 `code/` 內的訓練腳本完全同步。
"""
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

DATASET_CSV = DATA_DIR / "dataset_cleaned.csv"
MODEL_PATH = MODEL_DIR / "rf_model.pkl"
METRICS_PATH = MODEL_DIR / "metrics.json"

# 模型相關常數
INJURY_MAPPING = {"傷害": 1, "重傷": 2, "死亡": 3}
INJURY_REVERSE = {v: k for k, v in INJURY_MAPPING.items()}


def _load_metrics():
    """讀取 04_model_training.py 寫出的指標檔；缺檔時回傳 None。"""
    if not METRICS_PATH.exists():
        return None
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


_metrics = _load_metrics()

# 提供向後相容的常數，但實際值優先讀 metrics.json
if _metrics is not None:
    MODEL_MAE = int(_metrics.get("tuned_rf_mae", 0))
    DATASET_SIZE = int(_metrics.get("dataset_size", 0))
    MODEL_R2 = float(_metrics.get("tuned_rf_r2", 0.0))
    IMPROVEMENT_PCT = float(_metrics.get("improvement_pct_vs_null_mean", 0.0))
    NULL_MAE_MEAN = int(_metrics.get("null_mae_mean", 0))
    NULL_MAE_MEDIAN = (
        int(_metrics["null_mae_median"]) if _metrics.get("null_mae_median") is not None else None
    )
else:
    MODEL_MAE = 0
    DATASET_SIZE = 0
    MODEL_R2 = 0.0
    IMPROVEMENT_PCT = 0.0
    NULL_MAE_MEAN = 0
    NULL_MAE_MEDIAN = None
