"""
車禍精神慰撫金 AI 預測系統 - 主入口頁
執行：streamlit run app.py
"""
import streamlit as st

from config import DATASET_SIZE, MODEL_MAE
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
        "請先在終端機執行：`python train_model.py`"
    )
    st.stop()

st.success(f"✅ 模型已載入。訓練資料 **{DATASET_SIZE:,}** 筆，模型平均誤差約 **{MODEL_MAE:,} 元**。")

st.markdown(
    """
## 系統功能

### 🔮 1. AI 賠償預測
輸入車禍案件條件（傷亡程度、醫療費、看護費、酒駕、與有過失比例…），
系統會根據 **7,050 筆真實判決** 訓練的 Random Forest 模型，預估法官可能判賠的精神慰撫金金額。

### 💡 2. 如何減少賠償建議
分析影響判決金額的關鍵因素，並提供基於資料的策略建議：
- 模擬不同情境下的賠償差異
- 從歷史判決中找出降低金額的關鍵變數
- 依特徵重要性給出具體行動方向

### 📊 3. 資料探索
瀏覽資料分布、特徵重要性與不同條件下的判決統計。

---

👈 **請從左側選單選擇功能開始使用。**

### 模型成效摘要
| 指標 | 數值 |
|------|------|
| 訓練樣本 | 7,050 筆 |
| Null Model MAE | 494,720 元 |
| Random Forest MAE | 304,969 元 |
| 準確度提升 | **38.4%** |
| R-squared | 0.4618 |

### 三大影響因素
1. **看護費用 (Care_Fee)** — 39%
2. **傷亡嚴重度 (Injury_Level)** — 28%
3. **醫療費用 (Medical_Fee)** — 18%

---

> ⚠️ **法律免責聲明**：本系統預測結果僅供參考，不構成法律意見。實際判決金額由法官依個案綜合判斷。
"""
)
