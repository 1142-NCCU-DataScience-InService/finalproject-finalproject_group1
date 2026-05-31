# ⚖️ 車禍案件：精神慰撫金 AI 預測系統 (Predicting Mental Damages in Traffic Accidents)

本專案為國立政治大學資料科學課程期末專題，運用機器學習技術分析司法院裁判書開放資料，建立「車禍案件精神慰撫金」的預測模型，協助實務工作者與一般民眾預估合理的賠償金額，減少訴訟資源浪費。

> **目前狀態**：README 內容以目前 repo 可驗證的程式碼與資料 artifacts 為準。主要腳本位於 `code/`，路徑由 `code/config.py` 統一管理；`data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl` 已隨 repo 提供，可直接重跑建模與啟動展示。原始 RAR 與完整解壓資料未隨 repo 提供，需自行準備後才能重跑前段資料工程。

---

## 🧭 0. 重現狀態與專案結構 (Repro Status & Project Structure)

### 0.1 目前可重現狀態

經目前 repo 檔案檢查，**後段（建模與展示）可直接重現**，**前段（解壓與資料擷取）需自行準備司法院原始資料或解壓後 JSON 後才能重跑**。

| 步驟 | 腳本 | 輸入 | 產出 | 狀態 |
| --- | --- | --- | --- | --- |
| ① 解壓縮 | `code/01_extract_rar.py` | 原始 `.rar`（`SOURCE_DIR`） | 解壓後 JSON（`DEST_DIR`） | ⚠️ 需自備原始資料與 7-Zip |
| ② 建立資料集 | `code/02_build_dataset.py` | 解壓後 JSON（`DEST_DIR`） | `data/processed/car_accident_dataset.csv` + `SELECTED_DIR/` | ⚠️ 需先完成 ①；中繼 CSV 目前未隨 repo 提供 |
| ③ 清洗 / 特徵工程 | `code/03_exploratory_analysis.py` | `data/processed/car_accident_dataset.csv` | `data/processed/dataset_cleaned.csv` | ⚠️ 需先完成 ②；清洗後 CSV 目前已提供 |
| ④ 模型訓練 | `code/04_model_training.py` | `data/processed/dataset_cleaned.csv` | `models/rf_model.pkl` | ✅ 可直接執行 |
| ⑤ 互動展示 | `code/05_demo_app.py` | `models/rf_model.pkl` | Streamlit Web App | ✅ 可直接執行 |

> **為什麼 ①〜③ 不能從乾淨 clone 完整重現？**
> 司法院裁判書原始開放資料（RAR / JSON）體積龐大，且應依司法院開放資料條款自行下載，因此完整原始資料與解壓資料未隨 repo 發佈。只要依 [§2 原始資料說明](#-2-原始資料說明--data-source-documentation) 取得來源檔並設定路徑，即可由 ① 重跑到 ③。
>
> 由於 ③ 的產物 `data/processed/dataset_cleaned.csv` 已隨 repo 提供，**想直接驗證模型者可略過 ①〜③，直接執行 ④、⑤。**

### 0.2 建議專案結構

> 以下為目前 repo 與 `code/config.py` 對應的結構；實際路徑預設請以 **`code/config.py` 為準**，不一致處以 `config.py` 為主。

```text
final-project/
├── code/
│   ├── config.py                    # 路徑統一管理（相對路徑預設、可用環境變數覆寫）
│   ├── 01_extract_rar.py            # ① 解壓縮（需 7-Zip）
│   ├── 02_build_dataset.py          # ② 篩選車禍損賠案件、正則擷取特徵
│   ├── 03_exploratory_analysis.py   # ③ 清洗、EDA、特徵工程
│   ├── 04_model_training.py         # ④ Random Forest 訓練與評估
│   └── 05_demo_app.py               # ⑤ Streamlit 互動展示
├── data/
│   ├── raw/
│   │   ├── OPENDATA-原稿/              # 預設 SOURCE_DIR；原始 RAR 放置處
│   │   ├── Extracted_OpenData/         # 預設 DEST_DIR；解壓後 JSON 放置處
│   │   └── Selected_JSON(原始訓練資料)/ # 預設 SELECTED_DIR；命中案件 JSON 子集
│   └── processed/
│       ├── car_accident_dataset.csv    # ② 產出；目前未隨 repo 提供
│       └── dataset_cleaned.csv         # ③ 產出；目前已隨 repo 提供
├── models/
│   └── rf_model.pkl                 # ④ 產出（含模型與特徵欄位名）
├── docs/                            # 報告、簡報與專案文件
├── image/                           # 圖片輸出位置
├── results/                         # 表格與預測結果輸出位置
├── tests/                           # 測試 scaffold
├── requirements.txt
└── README.md
```

### 0.3 環境需求

- **Python**：Python 3.12
- **7-Zip**：僅 ①（解壓縮）需要
  - Windows：安裝官方 7-Zip，或設定 `SEVEN_ZIP`
  - macOS / Linux：安裝 `7z` 或 `7zz`，或設定 `SEVEN_ZIP`
- **套件**：`pip install -r requirements.txt`
  - 目前 `requirements.txt` 列出 `pandas`、`numpy`、`scikit-learn`、`joblib`、`streamlit`、`tqdm`
  - 版本尚未 pin 住，跨機器重現時建議記錄實際安裝版本
- **磁碟空間**：若要解壓完整裁判書開放資料，請預留原始壓縮檔數倍以上空間

---

## 🎯 1. 專案目標與輸入資料 (Input)

### 1.1 研究目標 (Goal)
- **核心問題**：精神慰撫金在實務上往往由法官依「自由心證」裁量，缺乏明確公式。
- **解決方案**：透過大數據分析過往判決，找出影響判決金額的關鍵特徵，並建立預測模型。

### 1.2 資料來源 (Data Source)
- **來源**：司法院裁判書開放資料（JSON 格式）
- **資料工程預設範圍**：`code/01_extract_rar.py` 的互動選單與範例指令以 2023–2025 年 RAR 作為近三年研究範圍
- **目前可驗證資料量**：
  - `data/raw/Selected_JSON(原始訓練資料)/`：目前 repo 中有 **7,531** 份命中案件 JSON
  - `data/processed/dataset_cleaned.csv`：清洗後模型資料為 **7,050** 筆、**81** 欄
  - `Year` 欄位來自司法院 `JYEAR`，目前清洗後資料範圍為民國 **107–114** 年

---

## 🗂️ 2. 原始資料說明 (Data Source Documentation)

本節說明「原始資料長什麼樣、如何取得、如何被程式讀取」，讓 ①〜③ 的步驟可被重現。

### 2.1 如何取得原始資料

1. 前往 **司法院資料開放平臺**：<https://opendata.judicial.gov.tw/>
2. 下載「裁判書」開放資料的壓縮檔（依月份提供，副檔名為 `.rar`）。
3. 將下載的 `.rar` 放入來源資料夾，並以 `code/config.py` 或環境變數 `SOURCE_DIR` 指向該資料夾。

> ⚠️ **授權與隱私**：原始裁判書屬司法院開放資料，請遵守其開放資料使用條款；資料本身可能含個資，請勿將原始檔或可識別個資的衍生資料公開上傳至 repo。

### 2.2 原始 RAR 檔命名規則

- 來源資料夾中的檔案為 `*.rar`，**檔名前 6 碼為西元年月 `YYYYMM`**（例如 `202401*.rar` 代表 2024 年 1 月）。
- `code/01_extract_rar.py` 以「檔名前 4 碼（西元年）」做年份過濾、以「前 6 碼（年月）」做月份分組。
- **同一月份若有多個版本**，程式只取檔名排序最大的最新版（`sorted(month_rars)[-1]`），避免重複解壓。

### 2.3 解壓後的目錄與檔案

- 每個月份解壓到 `DEST_DIR/YYYYMM/` 之下（保留原壓縮檔內的子目錄結構）。
- 解壓後每筆裁判書為一個 `.json` 檔；②（建立資料集）會針對 `DEST_DIR` 底下的月份資料夾，以 `rglob("*.json")` 遞迴掃描 JSON。

### 2.4 裁判書 JSON 欄位結構

每個 JSON 檔代表一份裁判書。本專案實際讀取並依賴下列欄位（其餘欄位未使用）：

| JSON 欄位 | 用途 | 在程式中的處理 |
| --- | --- | --- |
| `JTITLE` | 案由 | 篩選條件：必須包含「損害賠償」 |
| `JFULL` | 裁判書全文 | 篩選車禍關鍵字、並以正則擷取各項金額／特徵 |
| `JID` | 裁判書識別碼 | 取 `JID.split(",")[0]` 作為法院代碼；另存檔時將逗號換成底線 |
| `JYEAR` | 年度 | 寫入輸出欄位 `Year` |

> 註：`JID` 在程式中被視為逗號分隔字串。若日後司法院調整欄位格式，需同步檢查 `code/02_build_dataset.py` 的 `JID.split(",")` 邏輯。

### 2.5 「精選裁判書」子集（Selected_JSON）

- ② 在篩選出有效案件的同時，會把命中的原始 JSON 複製一份到 `SELECTED_DIR/`（`COPY_MATCHED_FILES = True`），檔名為 `JID` 將逗號換成底線後的 `{...}.json`。
- 目前 repo 中的 `data/raw/Selected_JSON(原始訓練資料)/` 有 **7,531** 份 JSON，可作為追溯資料來源的參考 artifact。
- `code/02_build_dataset.py` 的預設輸入仍是 `DEST_DIR` 底下的月份資料夾；`Selected_JSON` 目前不是該腳本的預設輸入目錄。

### 2.6 路徑設定（`config.py` 與環境變數）

所有主要路徑由 **`code/config.py`** 統一管理，預設使用專案內相對路徑，並可用環境變數覆寫。

| 環境變數 | 預設值 | 意義 | 對應步驟 |
| --- | --- | --- | --- |
| `SOURCE_DIR` | `data/raw/OPENDATA-原稿` | 原始 `.rar` 來源資料夾 | ① 輸入 |
| `DEST_DIR` | `data/raw/Extracted_OpenData` | 解壓後 JSON 的輸出資料夾 | ①→② |
| `SELECTED_DIR` | `data/raw/Selected_JSON(原始訓練資料)` | 命中案件的 JSON 複製目的地 | ② |
| `SEVEN_ZIP` | PATH 中的 `7zz` 或 `7z` | 7-Zip 執行檔路徑 | ① |

**設定範例：**

```bash
# macOS / Linux
export SEVEN_ZIP="/opt/homebrew/bin/7z"
export SOURCE_DIR="$HOME/judicial_opendata/rar"
export DEST_DIR="$HOME/judicial_opendata/extracted"
export SELECTED_DIR="./data/raw/Selected_JSON(原始訓練資料)"
```

```powershell
# Windows PowerShell
$env:SEVEN_ZIP    = "C:\Program Files\7-Zip\7z.exe"
$env:SOURCE_DIR   = "D:\judicial_opendata\rar"
$env:DEST_DIR     = "D:\judicial_opendata\extracted"
$env:SELECTED_DIR = ".\data\raw\Selected_JSON(原始訓練資料)"
```

---

## ⚙️ 3. 資料前處理管線 (Preprocessing Pipeline)

完整重現順序為 ①→②→③，最終產出模型輸入檔 `data/processed/dataset_cleaned.csv`。

### Step ① 解壓縮 — `code/01_extract_rar.py`

把 `SOURCE_DIR` 內的 `.rar` 以 7-Zip 解壓到 `DEST_DIR`。

```bash
python3 code/01_extract_rar.py                   # 互動選單
python3 code/01_extract_rar.py --years 2023-2025 # 只解壓特定西元年份
python3 code/01_extract_rar.py --all             # 全部解壓
```

特點：
- **斷點續傳**：若某月份資料夾解壓後的 JSON 數量已 > 1,000，視為已完成而自動跳過，可安全分多次執行。
- **只取最新版**：同月份多個壓縮檔只解壓檔名最大者。
- 解壓指令採 `7z x <rar> -o<dest> -y -aoa`（自動覆寫、不互動）。

### Step ② 建立資料集 — `code/02_build_dataset.py`

遞迴掃描 `DEST_DIR` 下各月份資料夾中的 JSON，篩選車禍損賠案件並以正則擷取特徵，輸出 `data/processed/car_accident_dataset.csv`，同時把命中 JSON 複製到 `SELECTED_DIR`。

**篩選條件（需同時成立）：**
1. `JTITLE` 含「損害賠償」
2. `JFULL` 含「車禍／交通事故／道路交通」任一關鍵字
3. 能從全文擷取到「精神慰撫金」金額（抓不到者跳過）

**擷取邏輯（皆以正則自 `JFULL` 取得）：**

| 輸出欄位 | 擷取目標 | 規則摘要 |
| --- | --- | --- |
| `Mental_Damage` | 精神慰撫金（目標 y） | 比對「精神慰撫金／非財產上損害／慰撫金 … 元」 |
| `Verdict_Total` | 判決給付總額 | 比對「被告應/須給付原告 … 元」「給付原告 … 元」 |
| `Medical_Fee` | 醫療費 | 比對「醫療費(用) … 元」 |
| `Care_Fee` | 看護費 | 比對「看護費(用) … 元」 |
| `Work_Loss` | 工作／勞動能力損失 | 比對「(勞動能力\|工作)損失 … 元」 |
| `Fault_Ratio` | 與有過失比例 | 比對「與有過失 … N%（或百分之 N）」，預設 0 |
| `Injury` | 傷亡類型 | 死亡/往生/殞命/不治→「死亡」；重傷/截肢/植物人→「重傷」；其餘→「傷害」 |
| `Drunk` | 酒駕 | 全文含 酒駕/酒後駕車/飲酒…駕 → 1，否則 0 |
| `Court` | 法院 | `JID.split(",")[0]` |
| `Year` | 年度 | `JYEAR` |

```bash
python3 code/02_build_dataset.py
# → data/processed/car_accident_dataset.csv
# → data/raw/Selected_JSON(原始訓練資料)/
```

### Step ③ 清洗與特徵工程 — `code/03_exploratory_analysis.py`

讀入 `data/processed/car_accident_dataset.csv`，輸出 `data/processed/dataset_cleaned.csv`。

1. **缺失值**：`Medical_Fee`、`Care_Fee`、`Work_Loss` 缺值補 0（視為未請求）；`Mental_Damage` 缺值則整筆刪除。
2. **異常值**：保留 `Mental_Damage` 介於 **10,000〜10,000,000** 元；各費用欄上限 **50,000,000** 元；`Fault_Ratio` 夾限於 0〜100。
3. **特徵編碼**：`Injury` 順序編碼為 `Injury_Level`（死亡=3、重傷=2、傷害=1、未知=0）；`Court` 做 One-Hot（`drop_first=True`）。
4. **特徵縮放**：對 `Medical_Fee`、`Care_Fee`、`Work_Loss`、`Mental_Damage` 做 `log1p`，新增 `*_log` 欄位以穩定訓練。

```bash
python3 code/03_exploratory_analysis.py
# → data/processed/dataset_cleaned.csv
```

### 中繼資料字典 (Data Dictionary)

**`car_accident_dataset.csv`（② 產出）原始欄位：**

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `JID` | 字串 | 裁判書識別碼（逗號分隔） |
| `Court` | 類別 | 法院代碼（`JID` 第一段） |
| `Year` | 整數 | 年度（`JYEAR`） |
| `Injury` | 類別 | 傷亡類型：死亡／重傷／傷害 |
| `Drunk` | 0/1 | 是否酒駕 |
| `Medical_Fee` | 數值（元） | 醫療費 |
| `Care_Fee` | 數值（元） | 看護費 |
| `Work_Loss` | 數值（元） | 工作／勞動能力損失 |
| `Fault_Ratio` | 數值（%） | 與有過失比例 |
| `Verdict_Total` | 數值（元） | 判決給付總額（**含目標值，建模時排除以防資料洩漏**） |
| `Mental_Damage` | 數值（元） | 精神慰撫金（**預測目標 y**） |

**`dataset_cleaned.csv`（③ 額外新增）欄位：**

| 欄位 | 說明 |
| --- | --- |
| `Injury_Level` | `Injury` 的順序編碼（3/2/1/0） |
| `Court_*` | `Court` 的 One-Hot 欄位（目前清洗後資料含多個法院代碼欄） |
| `Medical_Fee_log` / `Care_Fee_log` / `Work_Loss_log` / `Mental_Damage_log` | 對數轉換後特徵 |

---

## 🧠 4. 模型建構 (Modeling)

### 4.1 演算法選擇
針對具高度非線性關係的表格型特徵，選用樹狀模型 **Random Forest Regressor（隨機森林迴歸）**。

### 4.2 訓練策略
- **Train/Test Split**：80%（5,640 筆）/ 20%（1,410 筆）隨機切割。
- **超參數調整**：使用 `GridSearchCV` 做 3-fold 交叉驗證，評分指標為還原真實金額後的 MAE；搜尋範圍包含 `n_estimators=[100, 200]`、`max_depth=[8, 10, None]`、`min_samples_leaf=[2, 5]`、`min_samples_split=[2, 5]`、`max_features=[0.7, 1.0]`。
- **最佳超參數**：`n_estimators=200`、`max_depth=10`、`min_samples_leaf=2`、`min_samples_split=5`、`max_features=0.7`、`random_state=42`、`n_jobs=-1`。
- **防資料洩漏**：訓練特徵排除 `JID`、`Year`、`Injury`、原始目標欄、原始金額欄與 `Verdict_Total`；預測目標為 `Mental_Damage_log`，輸出時以 `np.expm1` 還原。
- **模型 artifact**：`models/rf_model.pkl` 是 `joblib` 檔，內容為 `{"model": rf, "features": X.columns.tolist()}`；目前保存 **72** 個模型輸入特徵。

### 4.3 基準模型 (Null Model)
- **策略**：無論案件特徵為何，一律「盲猜」訓練集的精神慰撫金平均值。
- **基準誤差**：MAE 為 **494,720 元**。

```bash
python3 code/04_model_training.py
# → models/rf_model.pkl（含模型與特徵欄位名）
```

---

## 📊 5. 成效評估 (Results)

### 5.1 評估指標
選用 **MAE（平均絕對誤差）**：相較 RMSE，更能直觀反映「預測金額與法官真實判決金額平均差了幾元」，在法律實務上最具解釋力。

### 5.2 顯著進步
- **Null Model MAE**：494,720 元
- **固定參數 Random Forest MAE**：304,966 元；R-squared：0.4618
- **GridSearchCV 交叉驗證 MAE**：360,725 元
- **調參後 Random Forest MAE**：303,619 元
- **進步幅度**：較盲猜基準提升 **38.6%**；相較固定參數 RF 的 MAE 降低 **1,348 元**
- **R-squared**：**0.4668**（以 log 目標計算）

### 5.3 特徵重要性（Top 5）
1. `Care_Fee_log`（看護費用對數）— 33.1%
2. `Injury_Level`（傷亡嚴重度）— 28.5%
3. `Medical_Fee_log`（醫療費用對數）— 21.2%
4. `Work_Loss_log`（工作損失對數）— 8.5%
5. `Court_CYEV`（法院 One-Hot 欄位）— 1.4%

> **洞察**：被害人所需的照護、醫療支出與傷亡嚴重程度越高，模型越傾向預測較高的精神慰撫金；法院 One-Hot 欄位則捕捉部分地區或法院差異。

---

## 💻 6. 系統展示與重現 (Demo & Reproducibility)

### 6.1 本機互動展示
使用 `Streamlit` 開發互動式 Web App，可輸入案件條件（傷亡程度、醫療費、是否酒駕等），即時呼叫模型試算賠償金額。

### 6.2 快速啟動（使用目前 checked-in artifacts）

```bash
pip install -r requirements.txt
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

若不想重新訓練，也可在 `models/rf_model.pkl` 已存在時直接啟動 App：

```bash
streamlit run code/05_demo_app.py
```

### 6.3 完整重現（含前處理，需自備原始資料）

```bash
# 0) 先依 §2 取得原始 RAR、設定 code/config.py / 環境變數
python3 code/01_extract_rar.py --years 2023-2025
python3 code/02_build_dataset.py
python3 code/03_exploratory_analysis.py
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

### 6.4 專案挑戰 (Challenges)
- **非結構化資料擷取**：司法文書格式極不統一，最大挑戰在於以正則表達式從中文裁判書中擷取各項賠償金額與案件特徵。
- **資料洩漏風險**：`Verdict_Total` 可能包含精神慰撫金本身，因此模型訓練時必須排除。
- **重現成本**：完整原始裁判書資料體積大，前段資料工程需要額外下載、解壓與磁碟空間。

---

## 🤖 7. 生成式 AI 協作歷程 (AI Collaboration Journey)

本專案保留的可驗證協作成果，主要體現在目前 repo 的工作流腳本、報告與展示 artifacts。README 僅列出 repo 內可直接檢查的文件位置，不重複未由檔案佐證的 prompt 時間線。

| 類型 | 目前檔案 | 說明 |
| --- | --- | --- |
| 程式工作流 | `code/01_extract_rar.py`〜`code/05_demo_app.py` | 從解壓、資料集建立、清洗、建模到 Streamlit 展示 |
| 路徑設定 | `code/config.py` | 集中管理 raw / processed / model 路徑與環境變數覆寫 |
| 書面報告 | `docs/report/車禍損害賠償預測_期末專題完整報告_正式版.docx` | 期末專題報告 artifact |
| 簡報 | `docs/slides/` | 期末報告與展示簡報 |
| 待辦紀錄 | `todo-list.md` | 專案後續事項紀錄 |

---

## 🧩 8. 已知問題與待辦 (Known Issues & TODO)

- [ ] `data/processed/car_accident_dataset.csv` 目前未隨 repo 提供；若要重跑 ③，需先由 ② 重新產生。
- [ ] 原始 RAR 與完整解壓資料未隨 repo 提供；①〜② 需自行下載司法院資料並準備足夠磁碟空間。
- [ ] 目前沒有正式自動化測試；`tests/` 僅保留 scaffold。
- [ ] `requirements.txt` 尚未鎖定版本；跨機器重現時可能需要補上 pinned versions。
- [ ] 正則擷取仍可能受裁判書格式差異影響；未來可加入抽樣人工驗證或更完整的 parser 測試。
- [ ] 未來可導入 LLM 輔助理解判決情節與抗辯內容，突破純正則表達式的限制。

---

## 👥 貢獻紀錄 (Changelog)

- 目前 README 已對齊 `code/` 編號工作流、`code/config.py` 路徑設定、checked-in artifacts 與目前可重算的模型指標。
- 目前 repo 可直接使用的核心 artifacts 為 `data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl`。
- 若未來重新產生 `data/processed/car_accident_dataset.csv`、`data/processed/dataset_cleaned.csv` 或 `models/rf_model.pkl`，請同步更新本 README 的樣本數、評估指標與特徵重要性。

---
*本專題為國立政治大學資料科學課程期末專案（第一組）*
