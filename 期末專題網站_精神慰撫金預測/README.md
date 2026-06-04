# ⚖️ 車禍精神慰撫金 AI 預測系統（網站子模組）

資料科學期末專題：基於司法院裁判書開放資料，建立精神慰撫金預測與訴訟策略建議的互動式網站。

> 本資料夾僅放 Streamlit 介面層程式，**不再保留訓練腳本、資料集、模型檔與 requirements**。
> 共用資源一律引用 repo root：
> - 資料集：`../data/processed/dataset_cleaned.csv`
> - 模型檔：`../models/rf_model.pkl`
> - 模型指標：`../models/metrics.json`（由 `code/04_model_training.py` 自動產生）
> - 套件相依：`../requirements.txt`

## 📁 結構

```
期末專題網站_精神慰撫金預測/
├── app.py                          # 主入口
├── config.py                       # 路徑設定（指向 repo root 的共用資源）
├── predictor.py                    # 模型載入與預測
├── generate_slides.py              # 簡報產生器
└── pages/
    ├── 1_🔮_AI賠償預測.py
    ├── 2_💡_減少賠償建議.py
    └── 3_📊_資料探索.py
```

## 🚀 快速開始

### 1. 安裝套件（在 repo root）
```powershell
pip install -r ..\requirements.txt
```

### 2. 確認模型已訓練
若 `..\models\rf_model.pkl` 或 `..\models\metrics.json` 不存在，先在 repo root 執行：
```powershell
python code\04_model_training.py
```

### 3. 啟動網站
```powershell
streamlit run app.py
```
瀏覽器會自動打開 http://localhost:8501

## 🧩 功能

| 頁面 | 說明 |
|------|------|
| 主頁 | 系統介紹與模型成效摘要（自動讀 `metrics.json`） |
| 🔮 AI 賠償預測 | 輸入案件條件，預估精神慰撫金 |
| 💡 減少賠償建議 | What-if 模擬 + 歷史統計 |
| 📊 資料探索 | 資料分布、特徵重要性、相關性分析 |

## 📊 模型表現
最新指標一律以 `..\models\metrics.json` 為準（由訓練腳本動態寫入）。
任何文件、簡報內出現的數字若與該檔不一致，請以 `metrics.json` 為唯一可信來源。

## ⚠️ 免責聲明
本系統預測結果僅供參考，不構成法律意見。
