import os
import shutil
from pathlib import Path


CODE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODE_DIR.parent

# Base directories
BASE_DIR = PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

def env_path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default)))

# Extraction paths
from typing import Optional

def resolve_seven_zip() -> Optional[str]:
    env_value = os.getenv("SEVEN_ZIP")
    if env_value:
        return env_value
    return shutil.which("7zz") or shutil.which("7z")
SOURCE_DIR = env_path("SOURCE_DIR", RAW_DATA_DIR / "OPENDATA-原稿")
DEST_DIR = env_path("DEST_DIR", RAW_DATA_DIR / "Extracted_OpenData")
SELECTED_DIR = env_path("SELECTED_DIR", RAW_DATA_DIR / "Selected_JSON(原始訓練資料)")

RAW_DATASET_CSV = PROCESSED_DATA_DIR / "car_accident_dataset.csv"
CLEANED_DATASET_CSV = PROCESSED_DATA_DIR / "dataset_cleaned.csv"

# Dataset files
INPUT_CSV = RAW_DATASET_CSV
OUTPUT_CSV = CLEANED_DATASET_CSV
MODEL_PATH = MODEL_DIR / "rf_model.pkl"




SEVEN_ZIP = resolve_seven_zip()
