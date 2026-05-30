import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

# Base directories
BASE_DIR = PROJECT_ROOT
MODEL_DIR = PROJECT_ROOT / "models"

def env_path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default)))

# Extraction paths
def resolve_seven_zip() -> str | None:
    env_value = os.getenv("SEVEN_ZIP")
    if env_value:
        return env_value
    return shutil.which("7zz") or shutil.which("7z")
SOURCE_DIR = env_path("SOURCE_DIR", PROJECT_ROOT / "OPENDATA-原稿")
DEST_DIR = env_path("DEST_DIR", PROJECT_ROOT / "Extracted_OpenData")
SELECTED_DIR = env_path("SELECTED_DIR", PROJECT_ROOT / "Selected_JSON(原始訓練資料)")

RAW_DATASET_CSV = PROJECT_ROOT / "car_accident_dataset.csv"
CLEANED_DATASET_CSV = PROJECT_ROOT / "dataset_cleaned.csv"

# Dataset files
INPUT_CSV = RAW_DATASET_CSV
OUTPUT_CSV = CLEANED_DATASET_CSV
MODEL_PATH = MODEL_DIR / "rf_model.pkl"




SEVEN_ZIP = resolve_seven_zip()
