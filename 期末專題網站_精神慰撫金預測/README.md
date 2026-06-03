# ⚖️ 車禍精神慰撫金 AI 預測系統

資料科學期末專題：基於司法院裁判書開放資料，建立精神慰撫金預測與訴訟策略建議的互動式網站。

## 📁 結構

```
期末專題網站_精神慰撫金預測/
├── app.py                          # 主入口
├── config.py                       # 路徑設定
├── predictor.py                    # 模型載入與預測
├── train_model.py                  # 模型訓練腳本
├── requirements.txt                # 套件依賴
├── data/
│   └── dataset_cleaned.csv         # 訓練資料 (7,050 筆)
├── models/
│   └── rf_model.pkl                # 已訓練模型
└── pages/
    ├── 1_🔮_AI賠償預測.py
    ├── 2_💡_減少賠償建議.py
    └── 3_📊_資料探索.py
```

## 🚀 快速開始

### 1. 安裝套件
```powershell
pip install -r requirements.txt
```

### 2. 準備資料與模型
將原始的 `dataset_cleaned.csv` 與 `rf_model.pkl` 複製進來：
```powershell
Copy-Item "..\000..期末專題報告簡報程式等(初版)\dataset_cleaned.csv" .\data\
Copy-Item "..\000..期末專題報告簡報程式等(初版)\models\rf_model.pkl" .\models\
```

或重新訓練模型：
```powershell
python train_model.py
```

### 3. 啟動網站
```powershell
streamlit run app.py
```
瀏覽器會自動打開 http://localhost:8501

## 🧩 功能

| 頁面 | 說明 |
|------|------|
| 主頁 | 系統介紹與模型成效摘要 |
| 🔮 AI 賠償預測 | 輸入案件條件，預估精神慰撫金 |
| 💡 減少賠償建議 | What-if 模擬 + 歷史統計，告訴你如何降低判賠 |
| 📊 資料探索 | 資料分布、特徵重要性、相關性分析 |

## 📊 模型表現
- 訓練樣本：7,050 筆判決
- Random Forest MAE：304,969 元
- 比 Null Model 提升 **38.4%**
- R²：0.4618

## ⚠️ 免責聲明
本系統預測結果僅供參考，不構成法律意見。
