"""
模型載入與預測工具（提供 Streamlit 各頁面使用）。
"""
from typing import Tuple

import joblib
import numpy as np
import pandas as pd

from config import MODEL_PATH, INJURY_MAPPING


def load_model() -> Tuple[object, list]:
    """載入模型與特徵欄位"""
    if not MODEL_PATH.exists():
        return None, None
    data = joblib.load(MODEL_PATH)
    return data["model"], data["features"]


def build_input_row(
    feature_names: list,
    injury: str,
    drunk: bool,
    fault_ratio: float,
    medical_fee: float,
    care_fee: float,
    work_loss: float,
    court_code: str = None,
) -> pd.DataFrame:
    """組出符合模型欄位順序的單筆輸入 DataFrame"""
    row = pd.DataFrame(0, index=[0], columns=feature_names)

    row["Injury_Level"] = INJURY_MAPPING.get(injury, 1)
    row["Drunk"] = 1 if drunk else 0
    row["Fault_Ratio"] = float(fault_ratio)
    row["Medical_Fee_log"] = np.log1p(max(medical_fee, 0))
    row["Care_Fee_log"] = np.log1p(max(care_fee, 0))
    row["Work_Loss_log"] = np.log1p(max(work_loss, 0))

    if court_code:
        col = f"Court_{court_code}"
        if col in feature_names:
            row[col] = True

    return row


def predict_amount(model, feature_names: list, **kwargs) -> float:
    """單筆預測，回傳真實金額（元）"""
    row = build_input_row(feature_names, **kwargs)
    pred_log = model.predict(row)[0]
    return float(np.expm1(pred_log))
