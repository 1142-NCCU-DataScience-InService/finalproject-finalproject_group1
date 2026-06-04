"""
車禍精神慰撫金 AI 預測系統 - 主入口頁
執行：streamlit run app.py

⚠️ 共用資源說明：本網站直接讀取 repo root 的 `data/processed/dataset_cleaned.csv`、
`models/rf_model.pkl` 與 `models/metrics.json`，請以 `code/04_model_training.py`
重新訓練來更新模型與指標，不要在本資料夾另外複製檔案。
"""
import streamlit as st

from config import (
    DATASET_SIZE,
    MODEL_MAE,
    MODEL_R2,
    IMPROVEMENT_PCT,
    NULL_MAE_MEAN,
)
from predictor import load_model

st.set_page_config(
    page_title="車禍精神慰撫金 AI 預測系統",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ 車禍案件：精神慰撫金 AI 預測系統")
st.caption("資料科學期末專題｜資料來源：司法院裁判書開放資料 (民國 112–114 年)")

model, _ = load_model()

if model is None:
    st.error(
        "⚠️ 找不到訓練好的模型檔案 `models/rf_model.pkl`。\n\n"
        "請先在 repo root 執行：`python code/04_model_training.py`"
    )
    st.stop()

if DATASET_SIZE == 0:
    st.warning(
        "尚未產生 `models/metrics.json`，下方數字將顯示為 0。"
        "請執行 `python code/04_model_training.py` 以產生最新指標。"
    )

st.success(f"✅ 模型已載入。訓練資料 **{DATASET_SIZE:,}** 筆，模型平均誤差約 **{MODEL_MAE:,} 元**。")

st.markdown(
    f"""
## 系統功能

### 🔮 1. AI 賠償預測
輸入車禍案件條件（傷亡程度、醫療費、看護費、酒駕、與有過失比例…），
系統會根據 **{DATASET_SIZE:,} 筆真實判決** 訓練的 Random Forest 模型，預估法官可能判賠的精神慰撫金金額。

### 💡 2. 如何減少賠償建議
分析影響判決金額的關鍵因素，並提供基於資料的策略建議：
- 模擬不同情境下的賠償差異
- 從歷史判決中找出降低金額的關鍵變數
- 依特徵重要性給出具體行動方向

### 📊 3. 資料探索
瀏覽資料分布、特徵重要性與不同條件下的判決統計。

---

👈 **請從左側選單選擇功能開始使用。**

### 模型成效摘要（自動讀取自 `models/metrics.json`）
| 指標 | 數值 |
|------|------|
| 訓練樣本 | {DATASET_SIZE:,} 筆 |
| Null Model MAE（盲猜平均值） | {NULL_MAE_MEAN:,} 元 |
| Random Forest MAE | {MODEL_MAE:,} 元 |
| 準確度提升 | **{IMPROVEMENT_PCT}%** |
| R-squared | {MODEL_R2:.4f} |

---

> ⚠️ **法律免責聲明**：本系統預測結果僅供參考，不構成法律意見。實際判決金額由法官依個案綜合判斷。
"""
)
